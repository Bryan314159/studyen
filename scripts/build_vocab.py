"""主脚本：读取 vocab.template.json 的待补全词条，
调用 DeepSeek + CMU dict 生成完整词条，合并到 vocab.json。

用法:
    export DEEPSEEK_API_KEY=sk-...
    python build_vocab.py

环境变量:
    DEEPSEEK_API_KEY  必填
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

# 允许直接 python build_vocab.py 运行
sys.path.insert(0, str(Path(__file__).resolve().parent))

from cmu_lookup import get_ipa  # noqa: E402
from prompts import (  # noqa: E402
    SYSTEM_PROMPT,
    VALID_CATEGORIES,
    build_user_prompt,
)


# 路径
ROOT = Path(__file__).resolve().parent.parent
VOCAB_PATH = ROOT / "data" / "vocab.json"
TEMPLATE_PATH = ROOT / "data" / "vocab.template.json"

# DeepSeek API（OpenAI 兼容）
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL = "deepseek-chat"

# 重试 / 限流
MAX_RETRIES = 3
RETRY_BACKOFF_SEC = 2
REQUEST_TIMEOUT = 30


def load_json(path: Path, default: Any) -> Any:
    """读取 JSON 文件；不存在则返回 default。"""
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: Any) -> None:
    """原子写：先写到 .tmp，再 rename，避免半写状态。"""
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    tmp.replace(path)


def call_deepseek(word: str, api_key: str) -> dict:
    """调用 DeepSeek 生成词条 JSON。失败抛 RuntimeError。"""
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(word)},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.3,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    last_err: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.post(
                DEEPSEEK_URL,
                headers=headers,
                json=payload,
                timeout=REQUEST_TIMEOUT,
            )
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            return json.loads(content)
        except (requests.RequestException, json.JSONDecodeError, KeyError) as e:
            last_err = e
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_SEC * attempt)
    raise RuntimeError(f"DeepSeek call failed for {word!r}: {last_err}")


def normalize_entry(word: str, llm: dict, ipa: str | None) -> dict:
    """校验并规范化 LLM 输出，组装词条。"""
    pos = str(llm.get("pos", "noun")).strip().lower()
    if pos not in {"noun", "verb", "adjective", "adverb"}:
        pos = "noun"

    category = str(llm.get("category", "core-concept")).strip().lower()
    if category not in VALID_CATEGORIES:
        category = "core-concept"

    try:
        difficulty = int(llm.get("difficulty", 2))
    except (TypeError, ValueError):
        difficulty = 2
    difficulty = max(1, min(3, difficulty))

    meaning_zh = str(llm.get("meaning_zh", "")).strip()
    meaning_en = str(llm.get("meaning_en", "")).strip()
    example_en = str(llm.get("example_en", "")).strip()
    example_zh = str(llm.get("example_zh", "")).strip()

    if not (meaning_zh and meaning_en and example_en and example_zh):
        raise ValueError(
            f"LLM returned incomplete fields for {word!r}: "
            f"zh={meaning_zh!r} en={meaning_en!r} "
            f"ex_en={example_en!r} ex_zh={example_zh!r}"
        )

    return {
        "id": word.lower().strip(),
        "word": word.strip(),
        "ipa": ipa,
        "pos": pos,
        "meaning_zh": meaning_zh,
        "meaning_en": meaning_en,
        "example_en": example_en,
        "example_zh": example_zh,
        "category": category,
        "difficulty": difficulty,
    }


def process_word(word: str, api_key: str) -> dict:
    """为单个词生成完整词条。"""
    print(f"  -> processing {word!r}")
    ipa = get_ipa(word)
    if ipa is None:
        print(f"     (no CMU pronunciation for {word!r})")
    llm = call_deepseek(word, api_key)
    return normalize_entry(word, llm, ipa)


def build() -> None:
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("ERROR: DEEPSEEK_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    vocab = load_json(
        VOCAB_PATH,
        default={"meta": {}, "entries": []},
    )
    template = load_json(
        TEMPLATE_PATH,
        default={"pending": []},
    )

    existing_words = {e["word"].lower() for e in vocab.get("entries", [])}
    pending: list[str] = []
    for item in template.get("pending", []):
        w = (item.get("word") or "").strip()
        if not w:
            continue
        if w.lower() in existing_words:
            print(f"  - skipping {w!r} (already in vocab)")
            continue
        pending.append(w)

    if not pending:
        print("No new words to process. Nothing to do.")
        return

    print(f"Processing {len(pending)} new word(s)...")
    new_entries: list[dict] = []
    for word in pending:
        try:
            entry = process_word(word, api_key)
            new_entries.append(entry)
            print(f"     OK  {word!r}  [{entry['category']}/d{entry['difficulty']}]")
        except Exception as e:  # noqa: BLE001
            print(f"     FAIL {word!r}: {e}", file=sys.stderr)

    if not new_entries:
        print("No entries were successfully generated. vocab.json left unchanged.")
        return

    # 合并并更新 meta
    vocab["entries"].extend(new_entries)
    vocab["meta"] = {
        "version": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "total_count": len(vocab["entries"]),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "deepseek+cmudict",
    }
    save_json(VOCAB_PATH, vocab)

    # 清空 template.pending（已处理的词不再保留）
    template["pending"] = []
    save_json(TEMPLATE_PATH, template)

    print(f"\nDone. Added {len(new_entries)} entries. Total: {len(vocab['entries'])}.")


if __name__ == "__main__":
    build()
"""CMU Pronouncing Dictionary 查询 + ARPAbet → IPA 转换。

API:
    get_ipa(word) -> str | None
        返回形如 "/ˈeɪdʒənt/" 的 IPA 字符串；若查不到则返回 None。
"""

from __future__ import annotations

import re

import cmudict

# 加载约 13 万词 CMU dict
_CMU = cmudict.dict()

# 特殊元音（依赖重音级别）
SPECIAL_VOWELS: dict[str, str] = {
    "AH0": "ə",
    "AH1": "ʌ",
    "AH2": "ʌ",
    "ER0": "ɚ",
    "ER1": "ɝ",
    "ER2": "ɝ",
}

# 默认元音映射
DEFAULT_VOWELS: dict[str, str] = {
    "AA": "ɑ",
    "AE": "æ",
    "AO": "ɔ",
    "AW": "aʊ",
    "AY": "aɪ",
    "EH": "ɛ",
    "EY": "eɪ",
    "IH": "ɪ",
    "IY": "i",
    "OW": "oʊ",
    "OY": "ɔɪ",
    "UH": "ʊ",
    "UW": "u",
}

# 辅音映射
CONSONANTS: dict[str, str] = {
    "B": "b",
    "CH": "tʃ",
    "D": "d",
    "DH": "ð",
    "F": "f",
    "G": "ɡ",
    "HH": "h",
    "JH": "dʒ",
    "K": "k",
    "L": "l",
    "M": "m",
    "N": "n",
    "NG": "ŋ",
    "P": "p",
    "R": "r",
    "S": "s",
    "SH": "ʃ",
    "T": "t",
    "TH": "θ",
    "V": "v",
    "W": "w",
    "Y": "j",
    "Z": "z",
    "ZH": "ʒ",
}

# 重音标记
STRESS_MARK: dict[int, str] = {0: "", 1: "ˈ", 2: "ˌ"}


def _phoneme_to_ipa(phoneme: str) -> tuple[str, int]:
    """把单个 ARPAbet 音素拆成 (IPA字符串, 重音级别)。

    例如 "EY1" -> ("eɪ", 1)，"B" -> ("b", 0)。
    """
    if not phoneme:
        return ("", 0)

    # 检查末尾的重音数字
    if phoneme[-1].isdigit():
        stress = int(phoneme[-1])
        base = phoneme[:-1]
    else:
        stress = 0
        base = phoneme

    # 优先查特殊元音（用带重音的原始 key，例如 "AH0"、"ER1"）
    if phoneme in SPECIAL_VOWELS:
        ipa = SPECIAL_VOWELS[phoneme]
    elif base in DEFAULT_VOWELS:
        ipa = DEFAULT_VOWELS[base]
    elif base in CONSONANTS:
        ipa = CONSONANTS[base]
    else:
        # 未知音素：退回小写字母（保守兜底）
        ipa = base.lower()

    return (ipa, stress)


def arpabet_to_ipa(phonemes: list[str]) -> str:
    """将 CMU ARPAbet 音素列表转换为 IPA 字符串（不带前后斜杠）。"""
    parts: list[str] = []
    for ph in phonemes:
        ipa, stress = _phoneme_to_ipa(ph)
        if stress == 1:
            parts.append("ˈ")
        elif stress == 2:
            parts.append("ˌ")
        parts.append(ipa)
    return "".join(parts)


def get_ipa(word: str) -> str | None:
    """查询单词或短语的 IPA 音标。

    策略：
    1. 单个 token（如 "agent"）：直接查 CMU dict。
    2. 多词短语 / 连字符复合词（如 "context window"、"fine-tuning"）：
       把每一节单独查 CMU，命中则拼接；至少一节命中就返回。
       这样 "context window" -> "/kˈɑntɛkst wˈɪndoʊ/"。

    Returns:
        形如 "/ˈeɪdʒənt/" 的字符串；查不到返回 None。
    """
    if not word:
        return None

    cleaned = re.sub(r"[^A-Za-z\s'-]", " ", word).strip()
    if not cleaned:
        return None

    # 把多词短语按空白拆分，再把每个 token 按连字符拆分
    tokens: list[str] = []
    for tok in cleaned.split():
        for piece in tok.split("-"):
            piece = re.sub(r"[^a-z]", "", piece.lower())
            if piece:
                tokens.append(piece)

    if not tokens:
        return None

    pieces_ipa: list[str] = []
    any_hit = False
    for tok in tokens:
        entries = _CMU.get(tok)
        if entries:
            pieces_ipa.append(arpabet_to_ipa(entries[0]))
            any_hit = True
        else:
            pieces_ipa.append(tok)  # 未命中保留原文占位

    if not any_hit:
        return None

    return "/" + " ".join(pieces_ipa) + "/"


if __name__ == "__main__":
    # 简单自测
    for w in ["agent", "token", "embedding", "RAG", "MCP",
              "context window", "transformer", "fine-tuning", "zero-shot",
              "nonexistentword12345"]:
        print(f"{w!r:25s} -> {get_ipa(w)}")
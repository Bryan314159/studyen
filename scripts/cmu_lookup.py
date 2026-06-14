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
    """查询单词的 IPA 音标。

    Args:
        word: 英文单词或短语。多词短语仅取第一个词查 CMU dict。

    Returns:
        形如 "/ˈeɪdʒənt/" 的字符串；查不到返回 None。
    """
    if not word:
        return None

    # 去除标点和多余空白
    cleaned = re.sub(r"[^A-Za-z\s'-]", " ", word).strip()
    if not cleaned:
        return None

    # CMU dict 的 key 是小写
    first_word = cleaned.split()[0].lower()
    entries = _CMU.get(first_word)
    if not entries:
        return None

    # 取第一个发音（通常为主要读音）
    return "/" + arpabet_to_ipa(entries[0]) + "/"


if __name__ == "__main__":
    # 简单自测
    for w in ["agent", "token", "embedding", "RAG", "MCP", "context window", "transformer"]:
        print(f"{w!r:20s} -> {get_ipa(w)}")
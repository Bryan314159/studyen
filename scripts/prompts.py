"""DeepSeek LLM 的 prompt 模板。"""

SYSTEM_PROMPT = """You are an AI/ML terminology expert building a vocabulary learning tool.
Given an English term (often related to AI, machine learning, or software engineering),
produce a JSON object with EXACTLY these fields and nothing else:

- pos: part of speech as a single word (one of "noun", "verb", "adjective", "adverb")
- meaning_zh: concise Chinese definition, 1-2 short sentences. Focus on the AI/tech meaning.
- meaning_en: English definition, 1 sentence.
- example_en: ONE natural English example sentence using the term in an AI/tech context.
- example_zh: Chinese translation of the example sentence.
- category: ONE of these exact strings:
  - "core-concept"   (basic AI/ML ideas: model, training, inference, etc.)
  - "architecture"   (model architectures: transformer, attention, etc.)
  - "training"       (training methods: fine-tuning, RLHF, distillation, etc.)
  - "deployment"     (serving, inference optimization: quantization, batching, etc.)
  - "evaluation"     (benchmarks, metrics: hallucination, perplexity, etc.)
  - "tooling"        (frameworks, libraries, infrastructure: PyTorch, MCP, RAG, etc.)
  - "agent"          (agent-related: prompt, tool use, planning, etc.)
- difficulty: integer 1, 2, or 3
    1 = basic term every AI learner should know
    2 = intermediate, requires some background
    3 = advanced / specialized

Output strictly valid JSON. No markdown, no commentary, no extra fields."""


USER_PROMPT_TEMPLATE = "Generate a vocabulary entry for the term: {word}"


# 类别枚举（用于校验 LLM 输出）
VALID_CATEGORIES = {
    "core-concept",
    "architecture",
    "training",
    "deployment",
    "evaluation",
    "tooling",
    "agent",
}


def build_user_prompt(word: str) -> str:
    return USER_PROMPT_TEMPLATE.format(word=word)
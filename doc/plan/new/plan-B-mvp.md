# Plan B: MVP 实现计划（当前）

> **状态**：pending（用户已批准，等待实现完成）
> **创建**：2026-06-14
> **归档来源**：`/Users/bryan/.claude/plans/llm-api-bright-frost.md`

## Context

用户正在学习 agent、AI coding 等内容，需要阅读大量英文项目文档、技术文档和 AI 资讯，但英语水平不高。目标是搭建一个工具，**针对 AI 领域的高频英文词汇**，帮助用户快速提升阅读能力和口语水平。

经过多轮讨论，确定以下 MVP 范围：
- 单 HTML 文件承载前端，单 Python 脚本调用 LLM API 生成词库
- 词库为 AI 领域英文术语，附音标、中文释义、英文例句及翻译
- 用户可在浏览器中浏览、查看详情、点击朗读、标记掌握度
- 通过 GitHub Actions 定时更新词库
- 用户的"手动添加新词"通过导出待补全列表 + GitHub 触发脚本补全的工作流完成

**为什么这个方案**：纯静态 + 离线优先、零服务器、零构建链路、隐私数据全本地，最小可行且可演进。

**计划执行约定**：
- 所有 plan mode 产出的 plan 存档到 `doc/plan/new/`
- 用户确认完成后，迁移到 `doc/plan/done/`
- 项目需求文档存放在 `doc/`
- 任何后续 plan 沿用相同的归档流程

---

## 架构概览

```
┌────────────────────────────────────────────────────┐
│                GitHub Repository                     │
│  ┌──────────────┐    ┌──────────────────────────┐   │
│  │ vocab.json   │◄───│ scripts/build_vocab.py   │   │
│  │ (生成结果)    │    │ - DeepSeek API           │   │
│  └──────┬───────┘    │ - CMU dict               │   │
│         │            └──────────────────────────┘   │
│         │                       ▲                    │
│         │                       │                    │
│  ┌──────┴──────────┐    ┌──────┴───────────────┐   │
│  │ vocab.template  │    │ .github/workflows/   │   │
│  │ (待补全词)       │    │ update-vocab.yml     │   │
│  └─────────────────┘    └──────────────────────┘   │
└────────────────────────────────────────────────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │   index.html          │
            │  - 列表浏览           │
            │  - 单词详情           │
            │  - Web Speech 朗读    │
            │  - 掌握度标记         │
            │  - 手动添加（导出）   │
            │  - localStorage       │
            └──────────────────────┘
```

---

## 项目结构

```
studyen/
├── index.html                          # 单 HTML 应用（所有 CSS/JS 内联或外联）
├── data/
│   ├── vocab.json                      # 生成后的最终词库（git tracked）
│   └── vocab.template.json             # 待补全词条（git tracked）
├── scripts/
│   ├── build_vocab.py                  # 主脚本：调 DeepSeek + CMU
│   ├── cmu_lookup.py                   # CMU dict 查音标 + ARPAbet→IPA
│   ├── prompts.py                      # LLM prompt 模板
│   ├── merge.py                        # 合并新词到 vocab.json
│   └── requirements.txt                # Python 依赖
├── .github/
│   └── workflows/
│       └── update-vocab.yml            # GitHub Actions 定时任务
├── .gitignore                          # 排除 .env, __pycache__
├── .env.example                        # 环境变量示例（不包含真实 key）
└── README.md                           # 项目说明 + 使用指南
```

---

## 关键文件设计

### 1. 词条数据 Schema (`data/vocab.json`)

```json
{
  "meta": {
    "version": "2026-06-14",
    "total_count": 300,
    "generated_at": "2026-06-14T03:00:00Z",
    "source": "deepseek+cmudict"
  },
  "entries": [
    {
      "id": "agent",
      "word": "agent",
      "ipa": "/ˈeɪdʒənt/",
      "pos": "noun",
      "meaning_zh": "智能体；能感知环境并自主执行动作的 AI 系统",
      "meaning_en": "An AI system that perceives its environment and takes autonomous actions to achieve goals.",
      "example_en": "The agent uses a tool to fetch the latest weather data before deciding what to wear.",
      "example_zh": "智能体使用工具获取最新天气数据，再决定穿什么。",
      "category": "core-concept",
      "difficulty": 2
    }
  ]
}
```

**字段说明**：
- `id`: 用单词本身作为 slug（去重 + URL 友好）
- `ipa`: 美式 IPA，由 CMU dict 转换
- `category`: 限定枚举 `[core-concept, architecture, training, deployment, evaluation, tooling, agent]`
- `difficulty`: 1/2/3 三档

### 2. 待补全词模板 (`data/vocab.template.json`)

```json
{
  "pending": [
    {"word": "RAG", "added_at": "2026-06-14"},
    {"word": "MCP", "added_at": "2026-06-14"}
  ]
}
```

### 3. Python 依赖 (`scripts/requirements.txt`)

```
requests>=2.31
cmudict>=1.0
python-dotenv>=1.0
```

### 4. DeepSeek API 调用 (`scripts/build_vocab.py`)

**关键逻辑**：
1. 加载 `vocab.template.json` 的待补全词
2. 加载已有 `vocab.json` 的所有 word 集合（去重）
3. 计算新词列表 = 待补全 - 已存在
4. 对每个新词：
   - 调用 `cmu_lookup.get_ipa(word)` 获取 IPA
   - 调用 DeepSeek API 获取释义/例句
   - 组装成 entry
5. 合并到 `vocab.json`，写回

### 5. Prompt 设计 (`scripts/prompts.py`)

```python
SYSTEM_PROMPT = """You are an AI/ML terminology expert.
Given an English term (often related to AI/ML), output a JSON object with these fields:
- pos: part of speech (e.g., "noun", "verb", "adjective")
- meaning_zh: concise Chinese definition (1-2 short sentences, focus on the AI/tech meaning)
- meaning_en: English definition (1 sentence)
- example_en: ONE natural English example sentence using the term in an AI/tech context
- example_zh: Chinese translation of the example sentence
- category: ONE of [core-concept, architecture, training, deployment, evaluation, tooling, agent]
- difficulty: 1 (basic term), 2 (intermediate), or 3 (advanced/specialized)

Output ONLY valid JSON. No markdown, no commentary."""
```

### 6. CMU dict 查询 (`scripts/cmu_lookup.py`)

```python
import cmudict

_CMU = cmudict.dict()

_ARPABET_TO_IPA = {
    "AA": "ɑ", "AE": "æ", "AH": "ə", "AO": "ɔ",
    "AW": "aʊ", "AY": "aɪ", "EH": "ɛ", "ER": "ɝ",
    "EY": "eɪ", "IH": "ɪ", "IY": "i", "OW": "oʊ",
    "OY": "ɔɪ", "UH": "ʊ", "UW": "u",
    "B": "b", "CH": "tʃ", "D": "d", "DH": "ð",
    "F": "f", "G": "ɡ", "HH": "h", "JH": "dʒ",
    "K": "k", "L": "l", "M": "m", "N": "n",
    "NG": "ŋ", "P": "p", "R": "r", "S": "s",
    "SH": "ʃ", "T": "t", "TH": "θ", "V": "v",
    "W": "w", "Y": "j", "Z": "z", "ZH": "ʒ"
}

def get_ipa(word: str) -> str | None:
    word_upper = word.upper().strip()
    entries = _CMU.get(word_upper)
    if not entries:
        return None
    return arpabet_to_ipa(entries[0])

def arpabet_to_ipa(arpabet: list[str]) -> str:
    # 处理重音标记（0/1/2）和音节分隔
    pass
```

**CMU 查不到时的 Fallback**：标记 `ipa` 为 `null`，UI 显示"无音标"或让用户手动补充。

### 7. 前端单 HTML (`index.html`)

**技术栈**：
- 纯 HTML + CSS + 原生 JavaScript（无框架）
- Tailwind CSS（CDN 引入，快速样式）
- Web Speech API（朗读）
- localStorage（用户状态）

**核心模块**：

```javascript
const STORAGE_KEY = 'studyen_state';

function loadState() {
  return JSON.parse(localStorage.getItem(STORAGE_KEY) ||
    '{"progress": {}, "pending": [], "settings": {"accent": "us", "rate": 0.9}}');
}

function saveState(state) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function speak(text, accent = 'us') {
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = accent === 'us' ? 'en-US' : 'en-GB';
  utterance.rate = state.settings.rate;
  speechSynthesis.speak(utterance);
}

function markStatus(wordId, status) {
  state.progress[wordId] = {
    status: status, // 'unknown' | 'fuzzy' | 'mastered'
    updated_at: new Date().toISOString()
  };
  saveState(state);
}

function exportPending() {
  const blob = new Blob([JSON.stringify({pending: state.pending}, null, 2)], {type: 'application/json'});
  // 触发下载
}
```

**localStorage 数据结构**：
```json
{
  "progress": {
    "agent": {"status": "fuzzy", "updated_at": "2026-06-14T..."}
  },
  "pending": [
    {"word": "RAG", "added_at": "2026-06-14"}
  ],
  "settings": {
    "accent": "us",
    "rate": 0.9
  }
}
```

### 8. GitHub Actions (`/.github/workflows/update-vocab.yml`)

```yaml
name: Update Vocab

on:
  schedule:
    - cron: '0 3 * * 1'  # 每周一凌晨 3 点（UTC）
  workflow_dispatch:
  push:
    paths:
      - 'data/vocab.template.json'

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r scripts/requirements.txt
      - name: Build vocab
        env:
          DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
        run: python scripts/build_vocab.py
      - uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "chore(vocab): update [skip ci]"
```

### 9. `.gitignore`

```
.env
__pycache__/
*.pyc
.DS_Store
```

### 10. `.env.example`

```
DEEPSEEK_API_KEY=sk-your-key-here
```

### 11. `README.md`

包含：
- 项目介绍
- 快速开始（clone → 打开 index.html）
- 如何手动添加新词的工作流
- 如何本地运行 Python 脚本
- GitHub Actions 配置说明（DEEPSEEK_API_KEY secret）

---

## 工作流（手动添加新词）

1. 用户在 HTML 中点击「手动添加」按钮
2. 输入单词（如 "RAG"），点击确认
3. 单词存入 localStorage 的 `pending` 数组
4. 用户点击「导出待补全词」按钮 → 下载 `vocab.template.json`
5. 用户提交 PR 或直接 push 到仓库 `data/vocab.template.json`
6. GitHub Actions 自动触发（或等待定时任务）
7. 脚本读取新词 → 调 DeepSeek + CMU → 合并到 `vocab.json`
8. 用户刷新 HTML 即可看到新词

---

## 实施步骤

按以下顺序实现（每个步骤独立可验证）：

### Phase 0: 项目初始化与文档归档（实现前必做）

- 创建 doc/ 目录结构
- 撰写 doc/REQUIREMENTS.md
- 归档历史 plan（本文件 + plan-A-extended.md）
- 执行 /init 并写入 plan 治理规则到 CLAUDE.md
- 提交初始化 commit

### Phase 1: 项目骨架 + git 初始化
- 创建目录结构
- 写 `.gitignore`、`.env.example`、`README.md` 框架

### Phase 2: Python 脚本开发
- `scripts/requirements.txt`
- `scripts/cmu_lookup.py`（CMU 查询 + ARPAbet→IPA）
- `scripts/prompts.py`（prompt 模板）
- `scripts/build_vocab.py`（主逻辑）
- 本地测试：手动添加 5 个测试词，运行脚本验证 JSON 输出

### Phase 3: GitHub Actions 配置
- `.github/workflows/update-vocab.yml`
- 在 GitHub 仓库设置 `DEEPSEEK_API_KEY` secret

### Phase 4: 前端 HTML 开发
- `index.html`（含 CSS + JS）
- 实现：列表浏览、详情展示、朗读、掌握度标记
- 实现：手动添加 + 导出待补全词
- 本地测试：用浏览器打开，验证所有交互

### Phase 5: 首次生成完整词库
- 准备 300 词种子清单
- 跑脚本生成 `vocab.json`
- 提交到仓库

### Phase 6: 验证
- 浏览器打开 HTML，确认词条显示、朗读、标记、添加流程
- 测试一次 GitHub Actions 完整运行

### Phase 7: 当前 plan 状态迁移
- 用户确认 MVP 可用后，把 `doc/plan/new/plan-B-mvp.md` 迁移到 `doc/plan/done/plan-B-mvp.md`

---

## 验证方式

### Python 脚本验证
```bash
cd scripts && pip install -r requirements.txt
echo '{"pending": [{"word": "agent", "added_at": "2026-06-14"}]}' > ../data/vocab.template.json
export DEEPSEEK_API_KEY=sk-xxx
cd .. && python scripts/build_vocab.py
cat data/vocab.json | python -m json.tool | head -50
```

### 前端验证
1. 浏览器打开 `index.html`（推荐 Chrome / Edge）
2. 首次进入：点击任意位置启用 Web Speech
3. 列表：确认 300 个词按分类显示
4. 朗读：点击单词卡片上的 🔊 按钮，听到发音
5. 掌握度：点击三档按钮，确认状态切换和持久化
6. 手动添加：输入 "test"，导出 JSON，确认格式正确

### GitHub Actions 验证
1. 推送 workflow 文件到 main 分支
2. 在 GitHub Actions 页面手动触发一次 workflow_dispatch
3. 检查运行日志，确认脚本执行成功

---

## 关键决策摘要

| 维度 | 决策 |
|---|---|
| LLM API | DeepSeek |
| 音标来源 | CMU dict (ARPAbet → IPA) |
| 初始词库规模 | 300 词 |
| 例句数量 | 每词 1 个英文 + 中文翻译 |
| 本地存储 | localStorage |
| 脚本调度 | GitHub Actions（每周一 + 手动 + template push 触发） |
| API Key 管理 | 环境变量（GitHub Secrets） |
| 手动添加工作流 | HTML 输入 → 导出 JSON → 提交仓库 → Actions 补全 |
| MVP 功能 | 列表 + 详情 + 朗读 + 掌握度 + 手动添加 |
| 项目位置 | `/Users/bryan/Agentic-Product-Engineer/studyen/` |

---

## 后续可演进（不在 MVP 范围）

- SRS 间隔重复算法
- 学习统计图表
- 暗色主题
- PWA 离线安装
- 浏览器扩展（一键收集网页生词）
- 移动端优化
- 云端同步（用 Supabase 等）
- 社区词库贡献
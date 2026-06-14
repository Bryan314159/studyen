# Plan C - 300 词种子清单准备

## Context

这是 Plan B（Studyen MVP）的 Phase 5（首次生成完整词库）的细化。MVP 的前 4 个 Phase 已实现并 commit（参见 git log），6 个 commit 全部就位，6 个手工示例词可正常显示。

当前需求：把示例词从 6 个扩展到约 300 个核心 AI 词汇，作为 GitHub Actions 调 DeepSeek 生成完整词条的种子。完成后用户只需 push 仓库、配置 Actions secret、运行 workflow，即可获得完整 300 词词库。

**本 plan 的精确范围**：
- 应用用户对 300 词清单的两项修订
- 写入 297 词种子到 `data/vocab.template.json`
- 在 `scripts/prompts.py` 中加一条缩写展开指令
- 归档本 plan 到 `doc/plan/new/`

**用户已确认**：
- 流行模型/产品（#271-290）全部从 Tier 1 降为 Tier 2
- 3 组缩写重叠采用「混合：只保留常用缩写」方案（保留 RAG/MoE/chain of thought，删 CoT/mixture of experts/retrieval-augmented generation）
- LLM prompt 需支持：缩写类词条释义在括号中给出全称

**最终词条数**：297

---

## 修改清单

### 修改 1: `data/vocab.template.json`

把 297 词种子清单写入 `pending` 数组，每项 `{"word": "...", "added_at": "2026-06-14"}`。

**缩写对最终保留情况**：

| 缩写对 | 保留 | 删除 |
|---|---|---|
| #75 mixture of experts / #76 MoE | #76 MoE | #75 mixture of experts |
| #201 chain of thought / #202 CoT | #201 chain of thought | #202 CoT |
| #204 RAG / #205 retrieval-augmented generation | #204 RAG | #205 retrieval-augmented generation |

**流行模型/产品（#271-290）Tier 调整**（全部 1→2）：

| # | Word | 原 | 新 |
|---|---|---|---|
| 271 | GPT-4 | 1 | 2 |
| 272 | GPT-4o | 1 | 2 |
| 273 | Claude | 1 | 2 |
| 274 | Claude 3.5 Sonnet | 1 | 2 |
| 275 | Llama | 1 | 2 |
| 276 | Llama 3 | 1 | 2 |
| 277 | Mistral | 1 | 2 |
| 278 | Mixtral | 2 | 2 |
| 279 | Gemma | 2 | 2 |
| 280 | Qwen | 2 | 2 |
| 281 | DeepSeek | 1 | 2 |
| 282 | DeepSeek R1 | 1 | 2 |
| 283 | Stable Diffusion | 1 | 2 |
| 284 | Midjourney | 2 | 2 |
| 285 | DALL-E | 2 | 2 |
| 286 | Whisper | 2 | 2 |
| 287 | PaLM | 3 | 2 |
| 288 | Gemini | 1 | 2 |
| 289 | o1 | 2 | 2 |
| 290 | Claude 3 Opus | 2 | 2 |

### 修改 2: `scripts/prompts.py`

在 `SYSTEM_PROMPT` 末尾追加缩写展开指令：

```
- If the input is an abbreviation or acronym, the meaning_zh and meaning_en
  fields must include the full form in parentheses on first mention
  (e.g., "RAG (Retrieval-Augmented Generation)" / "RAG（检索增强生成）").
  The example_en sentence should naturally use the abbreviation.
```

### 修改 3: 归档本 plan

把本 plan 文件复制到 `doc/plan/new/300-word-list.md`（按 `CLAUDE.md` 的「Plan Governance Rules」）。

---

## 不在本次修改范围

- `data/vocab.json`：保持 6 个手工示例，Actions 跑完后会被新生成结果覆盖
- `scripts/build_vocab.py`、`scripts/cmu_lookup.py`：逻辑已支持，无需改动
- `.github/workflows/update-vocab.yml`：无需改动（已支持 template push 触发）
- `index.html`：无需改动（已支持任意词条数）
- 6 个示例词：作为 297 词的一部分被新生成词条覆盖

---

## 实施步骤

### Step 1: 整理 297 词清单（纯数据准备）
把上一轮对话的 300 词按以下 10 维度分组，应用上述 2 项修订：
1. 基础概念 (50)
2. 模型架构 (50)
3. 训练方法 (40)
4. 推理/部署 (30)
5. 数据/Token (25)
6. Agent/工具 (30) — 删 #202 CoT → 29，加新词 1 个补齐 30
7. 评估 (25)
8. 安全/对齐 (20)
9. 流行模型/产品 (20)
10. 工具/框架 (10)

由于去掉了 3 个词（#75、#202、#205），需要从「Agent/工具」维度补充 1 个词到 30，或从其他维度补充。**决定**：从 评估 维度补 3 个，让评估保持 25；从 流行模型 维度补 1 个到 21；但用户已审过原 10 维度数量比例。最简单：把 297 作为最终数，不强行补 3 个。

### Step 2: 修改 `scripts/prompts.py`
定位到 `SYSTEM_PROMPT` 字符串末尾，在 `Output strictly valid JSON...` 这行之前插入缩写指令。

### Step 3: 写入 `data/vocab.template.json`
把 297 词放入 `pending` 数组。

### Step 4: 归档本 plan
`cp /Users/bryan/.claude/plans/effervescent-brewing-floyd.md /Users/bryan/Agentic-Product-Engineer/studyen/doc/plan/new/300-word-list.md`

### Step 5: commit + 推送
- `git add scripts/prompts.py data/vocab.template.json doc/plan/new/300-word-list.md`
- `git commit -m "feat(vocab): seed 297 core AI terms; expand abbreviations in prompt"`

---

## 验证方式

1. **JSON 校验**：
   ```bash
   python3 -m json.tool data/vocab.template.json > /dev/null && echo OK
   ```

2. **词条数核对**：
   ```bash
   python3 -c "import json; d=json.load(open('data/vocab.template.json')); print(len(d['pending']))"
   # 期望输出 297
   ```

3. **CMU 缩写抽查**（验证 RAG/MoE 等缩写 CMU 也能查到音标）：
   ```bash
   python3 -c "
   import sys; sys.path.insert(0, 'scripts')
   import cmu_lookup
   for w in ['RAG', 'MCP', 'LSTM', 'QLoRA', 'DPO', 'PPO', 'GRPO']:
       print(f'{w}: {cmu_lookup.get_ipa(w)}')
   "
   ```

4. **Prompt 修改自检**：
   ```bash
   python3 -c "
   import sys; sys.path.insert(0, 'scripts')
   from prompts import SYSTEM_PROMPT
   assert 'abbreviation' in SYSTEM_PROMPT.lower(), '缩写指令未添加'
   print('OK')
   "
   ```

5. **用户后续步骤**（不在本 plan 范围）：
   - `git push` 到 GitHub
   - 仓库 Settings → Secrets → Actions 添加 `DEEPSEEK_API_KEY`
   - GitHub Actions 页面手动触发 `Update Vocab` workflow
   - 跑完后验证 `data/vocab.json` 含 297 条且释义/例句质量

---

## 关键决策摘要

| 维度 | 决策 |
|---|---|
| 词条数 | 297（原 300，删 3 个缩写） |
| 流行模型 Tier | 全部 Tier 2（20 词） |
| 缩写对处理 | 保留 RAG/MoE，删 CoT + 两个全称（混合方案） |
| Prompt 改动 | 缩写类 meaning_zh/meaning_en 在括号中给出全称 |
| 现有 6 示例 | 自然包含在 297 词中（agent/prompt/embedding/transformer/token/fine-tuning 都在） |
| 不强行补 3 词 | 接受 297 词数（原维度比例略变，但用户已认可 300 词是目标量，297 误差可接受） |

---

## 完整词单

> 用户在上一轮对话中已审阅 300 词完整清单，本 plan 应用其反馈后得到 297 词：
> - 在原 300 词基础上：删 #75 mixture of experts、#202 CoT、#205 retrieval-augmented generation
> - 修改 #271-290 全部 Tier 从 1/2/3 统一为 2
> - 其他 277 词无变化
>
> 297 词完整列表（按 word 字母升序）会在 Step 1 数据准备时输出到 `data/vocab.template.json`，不再在 plan 中展开。

# Studyen

AI 领域英文词汇学习工具。打开 `index.html` 即可使用。

## ⚠️ 重要：必须通过 HTTP 访问

`index.html` 用 `fetch()` 加载 `data/vocab.json`，**直接双击 `file://` 打开会因 CORS 失败**。请用本地 HTTP 服务器：

```bash
# 在项目根目录
python3 -m http.server 8000
# 然后浏览器访问 http://localhost:8000
```

## 首次部署（生成词库）

项目自带 6 个示例词（`data/vocab.json`）用于本地 UI 验证。要生成完整的 AI 词汇库：

1. **推送到 GitHub**（首次）
   ```bash
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. **配置 Secret**：在 GitHub 仓库 `Settings` → `Secrets and variables` → `Actions` → `New repository secret`
   - Name: `DEEPSEEK_API_KEY`
   - Value: 你的 DeepSeek API key（[获取地址](https://platform.deepseek.com/)）

3. **加入种子词**：编辑 `data/vocab.template.json`，加入你想优先收录的 AI 术语，例如：
   ```json
   {
     "pending": [
       {"word": "transformer", "added_at": "2026-06-14"},
       {"word": "embedding", "added_at": "2026-06-14"},
       {"word": "fine-tuning", "added_at": "2026-06-14"}
     ]
   }
   ```
   `commit` 并 `push` 到 main 分支。

4. **触发 Actions**：进入仓库 `Actions` 标签 → 选择 `Update Vocab` workflow → `Run workflow`。Actions 会调 DeepSeek 生成完整词条，commit 到 `data/vocab.json`。

5. **下载/部署 `index.html`**：
   - 本地：从仓库 `git pull`
   - 部署：可推到 GitHub Pages（启用 Pages → 选择 main 分支 → 访问 `https://<user>.github.io/<repo>/`）

6. **验证**：浏览器打开 `index.html`（通过 HTTP），确认词条显示、🔊 朗读、掌握度标记都能用。

## 日常使用

### 添加新词
1. HTML 中点击「+ 手动添加」
2. 输入单词（例如 `RAG`）
3. 点击「导出待补全」下载 `vocab.template.json`
4. 把下载的文件覆盖到项目 `data/vocab.template.json`，commit & push
5. Actions 自动跑，刷新浏览器看到新词

### 复习
- 每张卡片有「不认识 / 模糊 / 掌握」三档按钮，状态存 localStorage
- 设置里可切换美式/英式发音和语速

## 本地跑词库构建（可选）

如果不方便用 GitHub Actions，也可在本地直接调 DeepSeek：

```bash
pip install -r scripts/requirements.txt
cp .env.example .env  # 填入 DEEPSEEK_API_KEY
export $(cat .env | xargs)
python scripts/build_vocab.py
```

## 项目结构

```
studyen/
├── index.html              # 单 HTML 应用
├── data/
│   ├── vocab.json          # 词库（示例数据 or Actions 生成）
│   └── vocab.template.json # 待补全词（用户输入）
├── scripts/
│   ├── build_vocab.py      # 主脚本：调 DeepSeek + CMU
│   ├── cmu_lookup.py       # CMU dict 查询
│   ├── prompts.py          # LLM prompt 模板
│   └── requirements.txt
├── .github/workflows/
│   └── update-vocab.yml
├── doc/                    # 需求与设计文档
│   ├── REQUIREMENTS.md
│   └── plan/{new,done}/
└── CLAUDE.md               # Claude 项目级指引
```

## 文档

- 需求文档：[`doc/REQUIREMENTS.md`](doc/REQUIREMENTS.md)
- 当前实现计划：[`doc/plan/new/plan-B-mvp.md`](doc/plan/new/plan-B-mvp.md)
- 历史方案：[`doc/plan/done/plan-A-extended.md`](doc/plan/done/plan-A-extended.md)
- 项目治理：[`CLAUDE.md`](CLAUDE.md)

## 技术栈

- **前端**：单 HTML + 原生 JS + Tailwind CDN + Web Speech API + localStorage
- **后端**：无（纯静态）
- **数据生成**：Python + DeepSeek API + CMU Pronouncing Dictionary
- **调度**：GitHub Actions

## License

TBD
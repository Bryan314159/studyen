# Studyen

AI 领域英文词汇学习工具。打开 `index.html` 即可使用。

## 快速开始

### 1. 使用（用户）
直接在浏览器中打开 `index.html` 即可：
```bash
# macOS
open index.html

# 或浏览器访问 file:// 路径
```

无需服务器、无需联网。所有学习数据保存在浏览器 localStorage 中。

### 2. 添加新词（用户）
1. 在 HTML 中点击「手动添加」
2. 输入单词（例如 `RAG`），确认
3. 点击「导出待补全词」下载 `vocab.template.json`
4. 把这个文件 commit 到仓库的 `data/vocab.template.json`
5. GitHub Actions 自动触发，调用 LLM 生成释义例句后合并到 `data/vocab.json`
6. 刷新浏览器，新词即出现

### 3. 更新词库（开发者）
```bash
# 安装依赖
pip install -r scripts/requirements.txt

# 配置 API key
cp .env.example .env
# 编辑 .env 填入 DEEPSEEK_API_KEY

# 在 data/vocab.template.json 中放入待补全词
# 然后运行
python scripts/build_vocab.py
```

### 4. 配置 GitHub Actions
在仓库 Settings → Secrets and variables → Actions 中添加：
- `DEEPSEEK_API_KEY`: DeepSeek API 密钥

Workflow 配置见 `.github/workflows/update-vocab.yml`，触发条件：
- 每周一凌晨 3 点（UTC）定时
- 手动触发（Actions 页面）
- `data/vocab.template.json` push 时自动触发

## 项目结构

```
studyen/
├── index.html              # 单 HTML 应用
├── data/
│   ├── vocab.json          # 词库（自动生成）
│   └── vocab.template.json # 待补全词（用户输入）
├── scripts/
│   ├── build_vocab.py      # 主脚本
│   ├── cmu_lookup.py       # CMU dict 查询
│   ├── prompts.py          # LLM prompt 模板
│   └── requirements.txt
├── .github/workflows/
│   └── update-vocab.yml
├── doc/                    # 需求与设计文档
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
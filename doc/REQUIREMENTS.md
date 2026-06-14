# Studyen 需求文档

> 创建于 2026-06-14，从初始讨论到 MVP 方案确定的全过程记录。

## 1. 项目背景

### 1.1 目标用户
- 正在学习 agent、AI coding 相关内容
- 阅读大量英文项目文档、技术文档、AI 资讯
- 英语水平不高，但需要快速提升 AI 领域的阅读与口语能力

### 1.2 核心痛点
- 英文阅读时大量生词阻碍理解
- AI 领域的专业术语在通用词典里查不到 AI 场景的释义
- 难以建立 AI 领域专属词汇量
- 没有针对 AI 场景的英语学习工具

### 1.3 核心需求
针对 AI 领域的英文词汇，构建一个工具，提供：
1. **AI 领域词汇整理与单词表**：覆盖 AI/ML 核心术语
2. **音标标注**：每个词附带 IPA 音标
3. **点击朗读**：点击单词可发音（默认美式）
4. **造句展示**：每个词在 AI 场景下的英文例句 + 中文翻译

---

## 2. 范围与边界

### 2.1 MVP 包含
- 列表浏览：按分类展示词条
- 单词详情：音标、释义、英文+中文例句
- 点击朗读：Web Speech API
- 掌握度标记：「不认识 / 模糊 / 掌握」三档
- 手动添加新词：HTML 输入 → 导出 JSON → 提交仓库 → Actions 补全

### 2.2 MVP 不包含
- 浏览器扩展（一键收集网页生词）
- SRS 间隔重复算法
- 学习统计图表
- 复习模式 / 闪卡
- 搜索 + 分类筛选（仅基础浏览）
- 暗色主题
- PWA 离线安装
- 移动端深度优化
- 云端同步（Supabase 等）
- 口语练习 / 发音评分
- 社区词库贡献

---

## 3. 约束

### 3.1 技术约束
- 前端：单 HTML 文件 + 原生 JS + Tailwind CDN + Web Speech API + localStorage
- 后端：无（纯静态）
- 数据更新：Python 脚本 + GitHub Actions
- 部署：GitHub Pages 或本地双击 HTML 打开

### 3.2 成本约束
- LLM API：DeepSeek（性价比高）
- 部署：GitHub Actions 免费层
- 本地存储：浏览器 localStorage（5-10MB）

### 3.3 隐私约束
- 用户学习数据（掌握度、待补全词）全在 localStorage，不上云
- 词库为公开仓库可见
- API Key 通过环境变量管理，不进仓库

---

## 4. 决策记录

### 4.1 方案演进

#### 方案 A：扩展方案（已否决）
**架构**：浏览器扩展 + 配套 Web App + 后端 + SRS + 统计
**否决原因**：
- 开发复杂度高（多端适配、后端运维）
- 周期长（预估 2-3 周）
- 主动收集能力强但代价是开发成本
- 用户偏好"快速可用"，无需完整学习管理系统

**结论**：留给后续演进，不进 MVP。

#### 方案 B：单 HTML + Python 脚本（采纳）
**架构**：
- 单 HTML 文件做前端
- Python 脚本调 DeepSeek + CMU dict 生成词库
- GitHub Actions 定时更新
- 手动添加通过导出 JSON 工作流
**优点**：
- 极简、零服务器、零构建
- 离线可用
- 1 周可上线
**取舍**：
- 失去主动收集能力（需切出去粘贴）
- 失去跨设备同步
- 失去复习提醒

### 4.2 关键技术决策

| 维度 | 决策 | 备选 |
|---|---|---|
| LLM API | DeepSeek | Claude / OpenAI / 本地模型 |
| 音标来源 | CMU dict（ARPAbet → IPA） | LLM 生成（不准确） / 词典 API（不稳定） |
| 初始词库规模 | 300 词 | 800 / 1500 |
| 例句数量 | 每词 1 个英文 + 中文翻译 | 2 个 / 3 个 |
| 本地存储 | localStorage | IndexedDB |
| 脚本调度 | GitHub Actions | 本机 cron / 手动 |
| API Key 管理 | 环境变量 | .env / 前端输入 |
| 手动添加工作流 | HTML → 导出 → 提交仓库 → Actions | 前端实时调 LLM |
| 词库生成方式 | LLM 直接生成词单 | 手动提供种子 |

### 4.3 讨论过程摘要

**Round 1（初步需求）**：用户描述痛点，提出工具需求清单。
**Round 2（方案 A 完整设计）**：用户选「浏览器扩展 + 配套 Web」「预制 AI 词库 + 手动补充」「SRS + 掌握度 + 统计」「不需要口语」。
**Round 3（方案 B 简化）**：用户提出「单 HTML + Python 定时更新」架构，方案 A 被否决。
**Round 4（MVP 决策细化）**：依次确定 LLM 调用时机、Key 管理、MVP 功能、词库生成策略、LLM 选型、音标来源、词库规模、手动添加工作流、例句中文翻译、例句数量、本地存储、脚本定时。
**Round 5（项目治理）**：要求把讨论整理成需求文档、plan 归档、初始化 CLAUDE.md。

---

## 5. 数据 Schema

### 5.1 词条（vocab.json entries）

```json
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
```

### 5.2 分类枚举
`[core-concept, architecture, training, deployment, evaluation, tooling, agent]`

### 5.3 难度枚举
`1`（基础）、`2`（中级）、`3`（高级）

### 5.4 待补全词模板（vocab.template.json）

```json
{
  "pending": [
    {"word": "RAG", "added_at": "2026-06-14"},
    {"word": "MCP", "added_at": "2026-06-14"}
  ]
}
```

### 5.5 localStorage 数据

```json
{
  "progress": {
    "agent": {"status": "fuzzy", "updated_at": "2026-06-14T..."},
    "prompt": {"status": "mastered", "updated_at": "..."}
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

---

## 6. 项目治理

### 6.1 Plan 管理
- 所有 plan mode 产出的 plan 存档到 `doc/plan/new/`
- 用户确认完成后，迁移到 `doc/plan/done/`

### 6.2 实现原则
- 不做未经授权的实现
- 有疑问必须先问，不做假设
- 文档存放约定：`doc/` 存放需求与设计文档

### 6.3 后续演进路线（按用户反馈触发）
1. SRS 间隔重复
2. 搜索 + 筛选
3. 学习统计
4. 浏览器扩展
5. PWA / 移动端
6. 云端同步

---

## 7. 验收标准（MVP）

- [ ] Python 脚本能调 DeepSeek 生成 300 词词库
- [ ] vocab.json 格式正确，可被 HTML 加载
- [ ] HTML 打开后能浏览所有词条
- [ ] 点击单词能朗读（Web Speech API）
- [ ] 掌握度标记可切换并持久化（刷新后保留）
- [ ] 手动添加单词能导出 JSON
- [ ] GitHub Actions 定时任务配置完成
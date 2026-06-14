# Plan A: 扩展方案（已否决）

> **状态**：rejected（用户否决）
> **创建**：2026-06-14
> **否决时间**：2026-06-14

## Context

本方案是讨论 Round 2 中提出的"完整功能"设计，包含浏览器扩展、配套 Web App、SRS 算法、学习统计等功能。用户最初选定此方案，但在 Round 3 中提出"单 HTML + Python 脚本"的极简方案（Plan B）后，本方案被否决。

否决原因：用户偏好"快速可用"的最小可行性方案，不需要完整学习管理系统。

---

## Round 2 用户决策

通过 AskUserQuestion 收集到以下偏好：

| 问题 | 回答 |
|---|---|
| 产品形态 | 浏览器扩展 + 配套 Web |
| 数据来源 | 预制 AI 词库 + 手动补充 |
| 学习功能 | 间隔重复 (SRS) + 掌握度标记 + 学习统计 |
| 口语能力 | 不需要，只要能听 |

---

## 设计要点

### 架构

```
┌──────────────────────────────────────────────┐
│         浏览器扩展 (Plasmo / WXT)            │
│  - 右键菜单加入单词本                         │
│  - 选中弹窗气泡                              │
│  - chrome.tts API 朗读                       │
│  - 同步数据到 Web App                         │
└──────────────────┬───────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│           Web App (PWA)                      │
│  - 词库浏览                                  │
│  - 单词详情                                  │
│  - SRS 复习模式 (SM-2 算法)                   │
│  - 学习统计面板                              │
│  - 手动添加/编辑                             │
└──────────────────┬───────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│         Backend (FastAPI / Fastify)          │
│  - 例句生成 (Claude API 代理)                │
│  - 词库 API                                  │
│  - 用户同步                                  │
└──────────────────────────────────────────────┘
```

### 核心功能清单

| 功能 | 实现方式 |
|---|---|
| 浏览器扩展 | Plasmo 框架，Chrome + Firefox 跨平台 |
| 选中即加入 | `chrome.contextMenus` + `chrome.scripting` |
| TTS | `chrome.tts.speak()`（扩展特权 API） |
| 词库浏览 | React + Vite + Tailwind |
| SRS 算法 | SM-2 简化版（20 行代码） |
| 学习统计 | Recharts 图表 |
| 跨设备同步 | FastAPI 后端 + SQLite |
| 例句生成 | Claude API（Anthropic） |

### 推荐技术栈

```
前端:    React 18 + Vite + TypeScript + Tailwind + shadcn/ui
扩展:    Plasmo (Chrome/Firefox)
后端:    Node.js + Fastify
数据库:  SQLite
状态:    Zustand + Dexie.js (IndexedDB)
统计:    Recharts
部署:    Vercel (前端) + Railway (后端)
```

### SM-2 算法核心

```typescript
function sm2(card, rating) {
  if (rating === 0) {
    card.interval = 1;
    card.repetitions = 0;
  } else {
    if (card.repetitions === 0) card.interval = 1;
    else if (card.repetitions === 1) card.interval = 6;
    else card.interval = Math.round(card.interval * card.easeFactor);
    card.repetitions += 1;
  }
  card.easeFactor = Math.max(
    1.3,
    card.easeFactor + (0.1 - (3 - rating) * (0.08 + (3 - rating) * 0.02))
  );
  card.nextReview = Date.now() + card.interval * 24 * 60 * 60 * 1000;
  return card;
}
```

### 升级路径（TTS）

| 阶段 | 方案 | 成本 |
|---|---|---|
| MVP | chrome.tts（扩展） + Web Speech（Web） | $0 |
| V2 | Azure Neural TTS | ~$16/百万字符 |
| V3 | ElevenLabs 自定义声音 | $5-22/月 |

---

## Round 3 否决原因

用户主动提出"单 HTML + Python 脚本"方案，本方案被否决。否决原因（从对话提取）：

1. **开发复杂度高**：浏览器扩展 + Web App + 后端三端开发
2. **周期长**：预估 2-3 周
3. **不必要的功能**：用户只要"快速可用"工具，不需完整学习管理系统
4. **成本**：Claude API + Vercel + Railway 累计月成本较高
5. **数据隐私**：后端意味着用户数据上云

---

## 被淘汰的关键能力

下列功能本方案提供但最终方案中放弃：

- ❌ 浏览器扩展一键收集网页生词
- ❌ SRS 间隔重复算法
- ❌ 学习统计图表
- ❌ 跨设备同步
- ❌ 桌面通知复习提醒
- ❌ 暗色主题切换
- ❌ 移动端 PWA 优化

---

## 后续可重新启用

如果用户在未来某个阶段需要上述能力，本方案可作为升级蓝图：
1. 先实现 Plan B（单 HTML + Python）
2. 用起来后，痛点会暴露（很可能是"切出去粘贴太麻烦"）
3. 此时启动本方案作为 V2 升级

---

## 关键决策对比

| 维度 | Plan A（此方案） | Plan B（MVP，已选） |
|---|---|---|
| 开发周期 | 2-3 周 | 1 周 |
| 主动收集 | ✅ 浏览器扩展 | ❌ 手动粘贴 |
| SRS | ✅ | ❌ |
| 学习统计 | ✅ | ❌ |
| 跨设备同步 | ✅ | ❌ |
| 复习提醒 | ✅ | ❌ |
| 例句质量 | Claude API 高质量 | DeepSeek 一次性生成 |
| 月成本 | ~$10-30 | < $1 |
| 数据隐私 | 部分上云 | 全本地 |
| 实现复杂度 | 高 | 低 |
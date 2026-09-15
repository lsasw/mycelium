# Mycelium · 菌丝 · 项目记忆

> **历史术语约定：** "Frontend Learning Hub" 是项目前身（v1 旧名，2026-09-05 改名为 Mycelium）。本文件作为项目历史叙事保留这些字样，后续批量替换脚本应跳过本文件。

> 最后更新：2026-09-05 | v3.0 — 由 Frontend Learning Hub（旧名，已废弃）升级为个人知识花园 Mycelium

---

## 1. 项目简介

**项目名称：** Mycelium · 菌丝（地下互联的常青笔记网络）

**项目定位：** 个人跨领域知识花园。55+ 张互联互通、持续打理的常青笔记，覆盖 AI、Java、架构、Python、心理学、投资等领域。形态：**常青笔记 + 双向链接 + D3 力导向图谱**。

**前身：** Frontend Learning Hub（v1：教程合集，iframe 加载）/ DevPortal 2.0 设计稿（v2：单文件 SPA）/ 现 v3.0 = Mycelium。

**GitHub：** [lsasw/mycelium](https://github.com/lsasw/mycelium)（✅ 2026-09-05 完成 rename；旧名 `frontend-learning-hub` 自动 301 redirect）

**目标：** 不再是「教程目录」，而是「持续生长的个人认知地图」。

---

## 2. 技术栈

| 层面 | 选型 | 说明 |
|---|---|---|
| 单文件 SPA | 原生 HTML/CSS/JS | `index.html` 自包含，**约 92 KB** |
| 数据驱动 | `garden-manifest.json` | **数据从 HTML 抽出**；55 张笔记元数据 |
| 图谱引擎 | D3.js v7 | jsdelivr CDN 加载，降级到 SVG 文案 |
| 状态 | `localStorage` | `favourites` / `recent` / `notes` / `streak` / `theme` / `view` |
| 字体 | 系统字体栈 + `Source Serif Pro` 衬线 | forest/sand 调色 |
| 外部依赖 | **仅 D3.js**（CDN），其他零依赖 | file:// 也能跑（除 D3） |

---

## 3. 核心架构

### 3.1 数据模型（`garden-manifest.json`）

```jsonc
{
  "id": "rag-fundamental",          // 全局唯一
  "title": "...", "cat": "AI · RAG",
  "maturity": 0-5,                  // 0 待开荒 / 1-2 种子 / 3 抽芽 / 4-5 常青
  "evergreen": true|false,
  "created": "...", "updated": "...", "tended": "...",  // ISO 日期
  "url": "相对路径.html",
  "desc": "一句话描述",
  "tags": ["..."], "related": ["id1", "id2"]
}
```

### 3.2 三视图

- 📇 **卡片**：默认，按成熟度分组
- 🌐 **图谱**：D3.js 力导向，仅展示 `maturity>0` 或有 `related` 的节点
- ⏳ **时间线**：按 `updated` 月份倒序分组

### 3.3 核心交互

- ⌘K 命令面板（支持 `tag:` `cat:` 前缀）
- 🎲 随机漫步（仅已打理笔记池）
- 反向链接面板（自动构建）
- 我的私人笔记（textarea，400ms 防抖保存）
- 主题切换 / 视图模式持久化 / 连续访问 streak

---

## 4. 目录结构

```
mycelium/
├── index.html                       # 🔑 花园主入口（含内嵌 manifest）
├── garden-manifest.json             # 🍄 数据源
├── README.md                        # GitHub README（v3 已更新）
├── overview.md                      # 设计交接文档（v2/v3 合并保留）
│
├── ai-agent/  architecture/  big-data/  design-system/
├── finance/  frontend/  infra/  java/  python/
├── ai-tools/
│   └── *.html                       # 单文件自包含教程
├── <根目录 *.html>                  # 老教程（被讨厌的勇气等）
│
├── .workbuddy/memory/
│   ├── MEMORY.md                    # 本文件
│   └── YYYY-MM-DD.md                # 每日工作日志
│
└── .github/workflows/deploy.yml     # GitHub Pages 部署
```

---

## 5. 新增笔记的流程

1. 创建 `<分类>/新笔记.html`（单文件、内联样式、零外部 CDN）
2. **必须改两处**：`garden-manifest.json` 的 `notes[]` **和** `index.html` 内嵌的
   `<script type="application/json" id="manifest-data">`。内嵌那份是为了绕开 file:// 下
   `fetch` 被禁止的限制；**只改一处不生效**（页面读的是内嵌那份）
3. 跑一致性校验脚本，比对两份 `notes` 的 `id` 序列是否完全一致
4. commit + push，等 GitHub Pages workflow 绿；再用 curl/无头浏览器验证线上
5. 已打理笔记必须填 `maturity > 0` + `related[]`，并保持双向（在另一张的 `related` 也加上自己）

---

## 6. 关键约定

- 文件命名可中文（如 `分布式系统-交互式学习平台.html`），不强求 ASCII
- 单文件 HTML：CSS inline、SVG inline、无外部 CDN
- 主题色：森林绿 + 砂纸色 + 琥珀提醒；与"开发者蓝调"区分
- 字体：sans 默认系统栈；详情页 h1/h2 可用衬线字体提升气质
- 不引入框架（Vue/React/Next 等），仅在最末端的花园主入口用 D3

---

## 7. 历史 / 待清理

- ✅ 30+ 子页面 footer 批量替换完成（2026-09-05，34 文件 49 处，统一为 "Mycelium · 菌丝"）。
- ✅ 本地所有 GitHub URL 已切换 `lsasw/frontend-learning-hub` → `lsasw/mycelium`（4 个文件；此处旧 URL 仅作迁移说明）。
- ✅ GitHub 端仓库 rename 已完成（2026-09-05）：`lsasw/frontend-learning-hub` → `lsasw/mycelium`；GitHub 自动 301 redirect 旧链，零断链。
- 旧 v1 SPA 架构（iframe + hash 路由）已废弃，新数据通过 manifest 驱动。

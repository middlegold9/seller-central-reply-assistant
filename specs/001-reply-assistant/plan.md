# Plan: Seller Central 买家消息 AI 回复助手

> 技术实现计划（Spec-Kit plan + Superpowers writing-plans 风格）。

## 技术栈
- 前端：Plasmo（Chrome MV3）；TypeScript + React；content script / popup / options / background SW。
- 后端（可选自托管）：FastAPI（Python）；LLM 可配置（OpenAI/Claude/本地）；RAG 用向量库（DuckDB + 嵌入）。
- 存储：`chrome.storage.local`（用户设置/Key）；后端 Postgres/DuckDB（学习库、埋点）。
- 测试：前端 Vitest；后端 pytest。

## 目录结构
```
seller-central-reply-assistant/
├── package.json
├── plasmo.config.ts
├── .env.example
├── src/
│   ├── content.ts            # 注入按钮 + 解析 DOM
│   ├── background.ts         # SW：转发后端、管理状态
│   ├── popup/index.tsx       # 手动模式/设置快捷
│   ├── options.tsx           # 设置页（Key/品牌/语气/护栏）
│   ├── lib/
│   │   ├── dom.ts            # 选择器 + 解析（可配置兜底）
│   │   ├── message.ts        # 与 background/后端通信
│   │   └── types.ts          # Draft/Context/RiskFlag 类型
│   └── backend/
│       ├── app.py            # FastAPI 入口
│       ├── llm.py            # LLM 调用 + prompt 组装
│       ├── guardrails.py     # 政策护栏引擎（规则库）
│       ├── classify.py       # 消息分类
│       ├── enrich.py         # 调 sp-api-mcp 丰富上下文
│       └── learn.py          # 学习库写入/检索
└── tests/
    ├── test_guardrails.py    # 违规拦截单测
    ├── test_classify.py
    └── test_llm_draft.py
```

## 数据模型（data-model.md 摘要）
- `Context{orderId?, asin?, market, buyerLang, messageText}`。
- `Draft{draft, language, suggested_actions[], risk_flags[], confidence}`。
- `RiskFlag{level:block|warn|info, rule, detail}`。
- `ReplyRecord{ts, orderId?, category, adopted, risk_level}`（脱敏）。

## 契约（contracts）
- 后端 `/draft`：`POST {context, settings}` → `Draft`。
- 后端 `/classify` → `{category}`。
- 后端 `/enrich` → `{order_status, ship_status, buyer_name?}`（经 MCP RDT）。
- 护栏输出：`RiskFlag[]`；`block` 级使发送按钮禁用。

## 研究（research.md 摘要）
- Seller Central Buyer Messages DOM 结构（需实测选择器，做可配置 + 兜底手动粘贴）。
- 亚马逊 Buyer-Seller Messaging 政策红线（索评/站外/操纵排名/移除差评）。
- Plasmo MV3 通信：content ↔ background ↔ 后端 HTTPS。
- RAG：历史高采用率回复建索引，新会话检索相似案例。

## 关键风险与缓解
- DOM 常变 → 选择器可配置 + 探测失败兜底手动粘贴。
- 亚马逊限制自动化 → 仅「辅助生成、人工发送」。
- LLM 幻觉给错物流 → 强制以 sp-api 实数据为准，不编。

## 快速开始（quickstart.md 摘要）
1. `pnpm install && pnpm dev`（Plasmo 开发模式）。
2. `chrome://extensions` 加载 `build/chrome-mv3-dev`。
3. 设置页填 LLM Key 与品牌语气。
4. 打开 Seller Central 买家消息页，点「AI 草稿」。

## 实现顺序（依赖）
1. Plasmo 骨架 + 设置页 + 类型（US5/US9 基础）
2. content.ts 注入 + DOM 解析（US1/US2 前置）
3. 后端 llm.py + /draft（US3）
4. guardrails.py + 双跑护栏（US2/FR4）
5. classify + 高风险转人工（US4/FR5）
6. enrich（接 MCP，FR7）+ learn（RAG，US6）
7. 测试 + 手动验收

# seller-central-reply-assistant

> **Seller Central 买家消息 AI 回复助手（Chrome 插件 + 后端）** —— 在亚马逊卖家后台 Buyer Messages 页面一键生成「合规、贴合品牌、带政策风险提示」的回复草稿，人工确认后发送。
> 最「当场击穿」的 Demo：客服是时差 + 量大的刚需，打开后台就有 AI 草稿，使用率不用愁。

> 状态：**后端已落地 + 19/19 单测通过**（FastAPI）；前端为完整 Plasmo MV3 代码。

---

## 1. 这个工具解决什么问题

跨境卖家的客服有四大痛点，直接导致评分下降、ODR 恶化、封号风险：

- **时差**：美国买家白天发消息 = 中国运营半夜，24h 内未回复伤 ODR / 评分。
- **量大**：促销季消息暴涨，手工逐条写，新人话术参差易踩线。
- **政策红线**：亚马逊严禁索评、引导站外、操纵排名、承诺删差评；违规即封号。
- **多语言**：买家用英 / 西 / 德 / 日等，卖家需对应语言准确回复。

本工具把 AI 直接注射进 Seller Central 的 Buyer Messages 页面：自动抓上下文 → 生成合规多语言草稿 + 政策风险标记 → **人类确认后**走官方通道发送。**AI 只生成、不自动发送**，从根本上规避违规。

---

## 2. 核心能力

| 能力 | 说明 |
|---|---|
| **政策护栏引擎** | 分级规则库：`block`（索评 / 站外 / 删评 / 返现 / 虚假物流，硬阻断发送）、`warn`（过度承诺 / 未授权折扣，标红提醒）、`info`（建议用官方模板）。输入侧（买家消息）+ 输出侧（AI 草稿）各跑一遍。 |
| **消息分类** | `logistics` / `quality` / `refund` / `feedback_removal` / `a_to_z` / `other`，驱动模板与动作建议。 |
| **高风险转人工** | 命中 A-to-z 索赔、差评移除请求、法律 / 威胁 → 不生成发送草稿，改为「建议人工处理」卡片 + 要点摘要。 |
| **LLM 草稿生成** | 多语言对齐（检测买家语言 → 同语言回）；品牌语气可配置；输出结构化 JSON。 |
| **上下文丰富（FR7）** | 可选经 `sp-api-mcp-server` 调用 `spapi_orders_get` / `spapi_orders_buyer_info`(RDT) 拿到真实订单 / 物流状态，避免 LLM 编造物流信息。 |
| **学习库 RAG** | 高采用率 + 低风险的历史回复脱敏建索引，新会话检索相似案例提升话术质量。 |
| **浏览器注入** | Plasmo MV3 插件：Content Script 注入「AI 草稿」按钮 + 浮层；`block` 级风险直接禁用发送按钮。 |

---

## 3. 端到端链路

```
[卖家打开 Seller Central 买家消息页]
  └─ Content Script 解析 DOM（买家最新消息 / 订单号 / ASIN / 语言）
       └─ 点击「AI 草稿」
            └─ 后端（可选调用 sp-api-mcp 丰富上下文）
                 ├─ 政策护栏（输入侧）
                 ├─ 分类 + 风险分级
                 ├─ LLM 生成多语言草稿 + 建议动作
                 └─ 政策护栏（输出侧，标红 / 阻断高危）
                      └─ 浮层渲染草稿 + 风险标签 + 动作按钮
                           └─ 卖家编辑 → 点「插入并发送」（走官方通道）
                                └─ 脱敏记录到学习库 + 埋点
```

---

## 4. 快速开始

### 4.1 后端（FastAPI）
```bash
cd seller-central-reply-assistant/backend
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
# 或装：fastapi uvicorn pydantic pydantic-settings httpx
cp .env.example .env   # 填 LLM_* 与可选 MCP_BASE_URL / MCP_TOKEN
uvicorn backend.app:app --reload --port 8000
```

### 4.2 前端（Plasmo 插件）
```bash
cd seller-central-reply-assistant
pnpm install          # 需要 Node 20+
pnpm dev              # 开发构建，chrome://extensions 加载 build 目录
pnpm build            # 生产构建，可上架 Web Store
```

---

## 5. 接口用法（后端）

所有接口返回 `Draft` JSON。后端 LLM 默认用 `stub`（无需真实 Key 即可跑通流程）；设 `llm_provider=openai|claude` 接真实模型。

### 5.1 分类
```bash
curl -X POST http://localhost:8000/classify \
  -H 'Content-Type: application/json' \
  -d '{"message_text":"怎么删除我的差评"}'
# → {"category":"feedback_removal","high_risk":true}
```

### 5.2 生成草稿
```bash
curl -X POST http://localhost:8000/draft \
  -H 'Content-Type: application/json' \
  -d '{
    "context": {
      "message_text": "Where is my order 111? It has not arrived.",
      "market": "US", "buyer_lang": "en", "order_id": "111"
    },
    "settings": {"llm_provider": "stub", "brand_name": "Acme", "tone": "friendly"}
  }'
```
返回示例：
```json
{
  "draft": "Hi, thanks for reaching out! ...",
  "language": "en",
  "suggested_actions": ["check_logistics", "offer_reship"],
  "risk_flags": [],
  "confidence": 0.9,
  "blocked": false,
  "needs_human": false,
  "category": "logistics"
}
```

### 5.3 丰富上下文（可选，依赖 sp-api-mcp-server）
```bash
curl -X POST http://localhost:8000/enrich \
  -H 'Content-Type: application/json' \
  -d '{"order_id":"111"}'
# → 返回订单状态 / 物流状态（用于草稿中给准确答复）
```

### 5.4 健康
```bash
curl http://localhost:8000/health   # {"status":"ok"}
```

---

## 6. 配置项（环境变量，前缀 `SC_`）

| 变量 | 说明 |
|---|---|
| `SC_LLM_PROVIDER` | `stub` / `openai` / `claude`（默认 stub） |
| `SC_LLM_API_KEY` | LLM API Key |
| `SC_LLM_BASE_URL` / `SC_LLM_MODEL` | 自建 / 第三方端点与模型名 |
| `SC_MCP_BASE_URL` / `SC_MCP_TOKEN` | 可选，连接 `sp-api-mcp-server` 丰富上下文 |
| `SC_GUARDRAIL_STRICTNESS` | `strict` / `normal` |

品牌设置（`BrandSettings`）还支持 `brand_name`、`tone`、`refund_limit`（自动可批退款上限，USD）、`guardrail_strictness`，可在请求体 `settings` 中覆盖。

---

## 7. 安全与合规（重中之重）

- **亚马逊政策**：绝不索评、绝不引导站外、不操纵排名；护栏 `block` 级硬阻断发送。
- **人类在环**：仅生成草稿，发送走官方通道（插件把草稿填回输入框，不模拟提交）。
- **数据最小化**：PII 不持久化；学习库只存脱敏片段。
- **本地优先**：前端 API Key 存 `chrome.storage.local`，不出用户设备。
- **审计**：所有生成记录留痕（时间 / 订单 / 风险等级）。

---

## 8. 测试

```bash
cd backend && source .venv/bin/activate
PYTHONPATH=src python -m pytest -q
# 19 passed —— 覆盖：护栏引擎（block/warn/info）、分类+高风险转人工、
#              LLM 草稿（语言对齐 + 双跑护栏）、上下文丰富、学习库 RAG
```

前端 `src/lib/dom.ts` 提供可配置选择器解析（订单号 / ASIN / 语言），并配有 `tests/dom.test.ts` 纯逻辑单测（在普通开发机 `pnpm install && pnpm test` 运行；本仓库的沙箱环境因 plasmo 原生依赖未能跑通该前端测试）。

---

## 9. 与另两个项目的关系

- 依赖 **sp-api-mcp-server** 的 `spapi_orders_*` 丰富上下文（可选增强）。
- 与 **amazon-ads-review-agent** 共享「政策护栏 / 审批网关 / 人类在环」原则。

---

## 10. 参考资料

- Buyer-Seller Messaging 政策：https://sellercentral.amazon.com/help/hub/reference/G200395540
- Plasmo：https://docs.plasmo.com
- 配套 MCP：https://github.com/middlegold9/sp-api-mcp-server
- 配套广告 Agent：https://github.com/middlegold9/amazon-ads-review-agent

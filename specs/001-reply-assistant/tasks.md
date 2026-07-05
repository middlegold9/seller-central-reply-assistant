# Tasks: Seller Central 买家消息 AI 回复助手

> Spec-Kit tasks（按用户故事；TDD：先测试后实现；`[P]` 可并行；精确路径 + 验证）。

## T1 — Plasmo 骨架与设置（US5/US9 基础）
- [ ] `package.json` + `plasmo.config.ts`：声明 Plasmo、React、MV3。
- [ ] `src/lib/types.ts`：`Context` / `Draft` / `RiskFlag` / `ReplyRecord`。
- [ ] `src/options.tsx`：设置页（LLM Key 存 `chrome.storage.local`、品牌名/语气/退款上限/护栏严格度）。
- [ ] `tests/test_types.py`（若用 ts 则 `src/lib/types.test.ts`）：类型构造断言。 **← TDD**
- **验证**：`pnpm dev` 能加载扩展；设置页可保存。

## T2 — 内容脚本注入与 DOM 解析（US1/US2 前置）
- [ ] `src/lib/dom.ts`：选择器配置 + 解析（订单号/ASIN/语言/消息文本）+ 兜底手动粘贴。
- [ ] `src/content.ts`：在 Buyer Messages 页注入「AI 草稿」按钮，点击收集 `Context` 发给 background。
- [ ] `src/background.ts`：SW 转发到后端 `/draft`，回写草稿到页面浮层。
- [ ] `tests/test_dom.py`：给定 mock DOM 字符串，断言解析正确。 **← TDD**
- **验证**：打开消息页出现按钮；点击拿到 `Context`。

## T3 — LLM 草稿生成（US3）
- [ ] `src/backend/llm.py`：组装 system（政策红线+品牌语气+场景模板）+ user（context+消息）；输出结构化 `Draft`。
- [ ] `src/backend/app.py`：`POST /draft` 返回 `Draft`。
- [ ] `tests/test_llm_draft.py`：mock LLM，断言输出含 `draft/language/suggested_actions`。 **← TDD**
- **验证**：测试绿；端到端拿到草稿。

## T4 — 政策护栏引擎（US2/FR4）`[P]`
- [ ] `src/backend/guardrails.py`：规则库（block/warn/info），对买家消息 + 草稿各跑一遍。
- [ ] `tests/test_guardrails.py`：用例含「给折扣换好评」→ block；「留个好评」→ block；过度承诺时效 → warn。 **← TDD**
- [ ] 前端：草稿浮层渲染 `risk_flags`，block 级禁用发送按钮。
- **验证**：合规率 ≥99%；block 用例发送按钮禁用。

## T5 — 分类与高风险转人工（US4/FR5）`[P]`
- [ ] `src/backend/classify.py`：logistics/quality/refund/feedback_removal/a_to_z/other。
- [ ] `tests/test_classify.py`：断言类别命中。 **← TDD**
- [ ] 命中 legal/threat/a_to_z/feedback_removal → 不生成发送草稿，显示「建议人工处理」卡片 + 摘要。
- **验证**：高风险会话显示转人工卡片。

## T6 — 多语言（US3/FR6）
- [ ] `llm.py` 增加语言检测 → 同语言生成；内置术语表避免机翻错误。
- [ ] `tests/test_llm_draft.py` 增多语言用例。
- **验证**：西语买家 → 西语回复。

## T7 — 上下文丰富（FR7）
- [ ] `src/backend/enrich.py`：调 `sp-api-mcp-server` 的 `spapi_orders_get` / `spapi_orders_buyer_info(RDT)`。
- [ ] `tests/test_enrich.py`：mock MCP，断言返回 `order_status/ship_status`。 **← TDD**
- **验证**：草稿含实时物流状态。

## T8 — 学习库 RAG（US6/FR10）
- [ ] `src/backend/learn.py`：发送后脱敏写入；新会话检索相似高采用率回复。
- [ ] `tests/test_learn.py`：断言检索返回相似案例。 **← TDD**
- **验证**：历史回复被索引并可检索。

## T9 — 打包与验收
- [ ] `pnpm build` 产出 `build/chrome-mv3-prod`；`.env.example` 补全。
- **验证**：手动走完 US1–US6 验收清单。

## 并行与检查点
- T4/T5 可并行；T6/T7/T8 依赖 T3/T4。
- **人工检查点**（executing-plans）：T4 护栏规则库完成后暂停，人工抽检违规用例拦截准确性，再继续。
- 每任务 RED→GREEN→REFACTOR；提交前 `pytest`/`vitest` 全绿（verification-before-completion）。

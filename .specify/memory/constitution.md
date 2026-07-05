# Constitution — seller-central-reply-assistant

> Spec-Kit 项目治理原则。任何代码前先有 spec → plan → tasks。

## 核心原则（FDE 方法论对齐）
1. **规格驱动**：先 `spec.md` → `plan.md` → `tasks.md`。
2. **嵌进工作流才有使用率**：插件必须零切换注入 Seller Central 买家消息页（呼应 FDE 文档 9.3）。
3. **人类在环 + 政策护栏**：绝不自动发送；草稿必须人工确认。亚马逊 Buyer-Seller Messaging 政策硬约束，护栏拦截致命违规。
4. **数据最小化 / 本地优先**：仅取生成回复所需上下文；API Key 存 `chrome.storage.local` 不出设备；PII 不持久化或脱敏。
5. **发送走官方通道**：插件只把草稿填回输入框，不模拟提交，避免违反 API ToS。
6. **可验证**：政策合规率、草稿可用率、响应时延、人工接管率可量化。
7. **可复盘**：每周复盘转人工/标红会话，提炼新规则进护栏库；采用率埋点反哺 prompt。
8. **YAGNI / DRY**：v1 只做单店铺 + 直连 LLM + 基础护栏。
9. **TDD**：护栏引擎与草稿生成先写失败测试。
10. **工作隔离**：git worktree 并行开发。

## 技术约束
- 前端：Plasmo（Chrome MV3）；TypeScript + React。
- 后端（可选自托管）：FastAPI（Python）。
- 默认分支：`main`；提交信息英文祈使句。
- 密钥绝不入库；提供 `.env.example`。

// 内容脚本：在买家消息页注入「AI 草稿」按钮，点击生成草稿并渲染浮层。
import type { Draft, Context } from "./lib/types";
import { parseContext, hasMessageNode } from "./lib/dom";
import { fetchDraft, getSettings } from "./lib/message";

function riskColor(level: string): string {
  if (level === "block") return "#d93025";
  if (level === "warn") return "#b06000";
  return "#1a73e8";
}

function renderOverlay(draft: Draft) {
  const root = document.getElementById("sc-reply-assistant-root");
  if (!root) return;
  root.innerHTML = "";
  const card = document.createElement("div");
  card.style.cssText =
    "position:fixed;right:16px;bottom:16px;width:380px;max-height:70vh;overflow:auto;" +
    "background:#fff;border:1px solid #dadce0;border-radius:12px;box-shadow:0 4px 24px rgba(0,0,0,.18);" +
    "padding:16px;font:14px/1.5 Arial,sans-serif;z-index:99999;";

  if (draft.needs_human) {
    const h = document.createElement("div");
    h.style.cssText = "color:#d93025;font-weight:600;margin-bottom:8px;";
    h.textContent = "⚠ 建议人工处理（高风险会话）";
    card.appendChild(h);
  }

  const body = document.createElement("div");
  body.style.cssText = "white-space:pre-wrap;margin:8px 0;";
  body.textContent = draft.draft || "（无草稿）";
  card.appendChild(body);

  for (const f of draft.risk_flags) {
    const r = document.createElement("div");
    r.style.cssText = `color:${riskColor(f.level)};font-size:12px;margin:2px 0;`;
    r.textContent = `[${f.level}] ${f.rule}: ${f.detail}`;
    card.appendChild(r);
  }

  const sendBtn = document.createElement("button");
  sendBtn.textContent = draft.blocked ? "已锁定（含红线，禁止发送）" : "复制并发送";
  sendBtn.disabled = draft.blocked;
  sendBtn.style.cssText =
    "margin-top:10px;width:100%;padding:8px;border:0;border-radius:8px;cursor:pointer;" +
    (draft.blocked ? "background:#f1f3f4;color:#9aa0a6;" : "background:#1a73e8;color:#fff;");
  sendBtn.onclick = () => {
    if (draft.draft) navigator.clipboard?.writeText(draft.draft);
  };
  card.appendChild(sendBtn);

  root.appendChild(card);
}

function injectButton() {
  if (document.getElementById("sc-ai-draft-btn")) return;
  const btn = document.createElement("button");
  btn.id = "sc-ai-draft-btn";
  btn.textContent = "🤖 AI 草稿";
  btn.style.cssText =
    "margin-left:8px;padding:6px 12px;border:0;border-radius:8px;background:#1a73e8;color:#fff;cursor:pointer;";
  btn.onclick = async () => {
    const ctx = parseContext(document) as Context;
    if (!ctx.message_text) {
      alert("未能自动识别消息内容，请确认在当前消息会话页。");
      return;
    }
    const settings = await getSettings();
    try {
      const draft = await fetchDraft(ctx, settings);
      if (!document.getElementById("sc-reply-assistant-root")) {
        const root = document.createElement("div");
        root.id = "sc-reply-assistant-root";
        document.body.appendChild(root);
      }
      renderOverlay(draft);
    } catch (e) {
      alert("生成草稿失败：" + (e as Error).message);
    }
  };
  const anchor =
    document.querySelector("[data-testid='message-actions']") ||
    document.querySelector(".message-toolbar") ||
    document.body;
  anchor.appendChild(btn);
}

// Plasmo 内容脚本入口
if (typeof document !== "undefined" && hasMessageNode(document)) {
  injectButton();
}

export {};

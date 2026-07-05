// 后台 Service Worker：代理后端请求（规避 CORS），并保管设置。
import type { Context, Draft, Settings } from "./lib/types";

type Req =
  | { type: "draft"; ctx: Context; settings: Settings }
  | { type: "classify"; message_text: string; settings: Settings };

chrome.runtime.onMessage.addListener((msg: Req, _sender, sendResponse) => {
  if (msg.type === "draft") {
    fetch(`${msg.settings.backend_url}/draft`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ context: msg.ctx, settings: msg.settings }),
    })
      .then((r) => r.json())
      .then((d: Draft) => sendResponse({ ok: true, draft: d }))
      .catch((e) => sendResponse({ ok: false, error: String(e) }));
    return true; // 异步响应
  }
  if (msg.type === "classify") {
    fetch(`${msg.settings.backend_url}/classify`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message_text: msg.message_text }),
    })
      .then((r) => r.json())
      .then((d) => sendResponse({ ok: true, data: d }))
      .catch((e) => sendResponse({ ok: false, error: String(e) }));
    return true;
  }
});

export {};

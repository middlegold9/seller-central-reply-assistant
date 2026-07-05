// 与后端通信：请求草稿 / 分类 / 丰富。
import type { Context, Draft, Settings } from "./types";

export async function fetchDraft(ctx: Context, settings: Settings): Promise<Draft> {
  const res = await fetch(`${settings.backend_url}/draft`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      context: ctx,
      settings: {
        brand_name: settings.brand_name,
        tone: settings.tone,
        refund_limit: settings.refund_limit,
        guardrail_strictness: settings.guardrail_strictness,
      },
    }),
  });
  if (!res.ok) throw new Error(`draft request failed: ${res.status}`);
  return (await res.json()) as Draft;
}

export async function fetchClassify(message_text: string, settings: Settings) {
  const res = await fetch(`${settings.backend_url}/classify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message_text }),
  });
  if (!res.ok) throw new Error(`classify request failed: ${res.status}`);
  return (await res.json()) as { category: string; high_risk: boolean };
}

export async function getSettings(): Promise<Settings> {
  const stored = await chrome.storage.local.get([
    "brand_name",
    "tone",
    "refund_limit",
    "guardrail_strictness",
    "backend_url",
  ]);
  return {
    brand_name: stored.brand_name || "YourBrand",
    tone: stored.tone || "friendly, professional, concise",
    refund_limit: stored.refund_limit ?? 20,
    guardrail_strictness: stored.guardrail_strictness || "strict",
    backend_url: stored.backend_url || "http://localhost:8000",
  };
}

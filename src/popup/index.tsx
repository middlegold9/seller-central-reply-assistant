// 弹窗：手动模式。粘贴买家消息，点生成拿草稿。
import { useState } from "react";
import type { Context, Draft, Settings } from "../lib/types";
import { fetchDraft, getSettings } from "../lib/message";

function DraftView({ draft }: { draft: Draft }) {
  return (
    <div style={{ padding: 8 }}>
      <pre style={{ whiteSpace: "pre-wrap" }}>{draft.draft || "（无草稿）"}</pre>
      {draft.risk_flags.map((f, i) => (
        <div key={i} style={{ color: f.level === "block" ? "#d93025" : "#b06000", fontSize: 12 }}>
          [{f.level}] {f.rule}: {f.detail}
        </div>
      ))}
      {draft.needs_human && <div style={{ color: "#d93025" }}>建议人工处理</div>}
    </div>
  );
}

export default function Popup() {
  const [text, setText] = useState("");
  const [draft, setDraft] = useState<Draft | null>(null);

  async function onGenerate() {
    const settings: Settings = await getSettings();
    const ctx: Context = { message_text: text, market: "US", buyer_lang: "en" };
    const d = await fetchDraft(ctx, settings);
    setDraft(d);
  }

  return (
    <div style={{ width: 360, padding: 12, fontFamily: "Arial" }}>
      <h3>Seller Central 回复助手</h3>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="粘贴买家消息…"
        rows={6}
        style={{ width: "100%" }}
      />
      <button onClick={onGenerate} style={{ marginTop: 8 }}>
        生成草稿
      </button>
      {draft && <DraftView draft={draft} />}
    </div>
  );
}

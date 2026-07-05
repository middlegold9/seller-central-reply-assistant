// 设置页：品牌名 / 语气 / 退款上限 / 护栏严格度 / 后端地址。
import { useState } from "react";
import type { Settings } from "./lib/types";
import { getSettings } from "./lib/message";

export default function Options() {
  const [s, setS] = useState<Settings | null>(null);

  if (!s) {
    getSettings().then(setS);
    return <div>加载中…</div>;
  }

  function update<K extends keyof Settings>(k: K, v: Settings[K]) {
    setS({ ...s, [k]: v });
    chrome.storage.local.set({ [k]: v });
  }

  return (
    <div style={{ maxWidth: 480, margin: "0 auto", padding: 16, fontFamily: "Arial" }}>
      <h2>回复助手设置</h2>
      <label>品牌名<input value={s.brand_name} onChange={(e) => update("brand_name", e.target.value)} /></label>
      <label>语气<input value={s.tone} onChange={(e) => update("tone", e.target.value)} /></label>
      <label>退款上限(USD)<input type="number" value={s.refund_limit} onChange={(e) => update("refund_limit", Number(e.target.value))} /></label>
      <label>护栏严格度
        <select value={s.guardrail_strictness} onChange={(e) => update("guardrail_strictness", e.target.value)}>
          <option value="strict">strict</option>
          <option value="normal">normal</option>
        </select>
      </label>
      <label>后端地址<input value={s.backend_url} onChange={(e) => update("backend_url", e.target.value)} /></label>
    </div>
  );
}

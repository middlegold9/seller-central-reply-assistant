// 在 Seller Central 买家消息页解析上下文。选择器可配置，解析失败兜底手动粘贴。
import type { Context } from "./types";

export const SELECTORS = {
  // 买家消息正文
  message: "[data-testid='message-body'], .buyer-message__body, .message-thread__message, .message-body",
  // 订单号（链接或文本）
  orderId:
    "[data-testid='order-id'], .order-id, a[href*='/orders/'], [data-order-id]",
  // ASIN
  asin: "a[href*='/dp/'], a[href*='/gp/product/']",
  // 站点标识
  market: "[data-marketplace], meta[name='marketplace']",
};

const ORDER_RE = /[0-9]{3}-[0-9]{7}-[0-9]{7}/;
const ORDER_HREF_RE = /orders\/([0-9]{3}-[0-9]{7}-[0-9]{7})/;
const ASIN_RE = /\/(?:dp|gp\/product)\/([A-Z0-9]{10})/;

export function parseContext(doc: Document, selectors = SELECTORS): Partial<Context> {
  const messageEl = doc.querySelector(selectors.message);
  const message_text = (messageEl?.textContent ?? "").trim();

  const orderEl = doc.querySelector(selectors.orderId);
  const order_id =
    (orderEl?.getAttribute("href")?.match(ORDER_HREF_RE)?.[1]) ??
    orderEl?.textContent?.match(ORDER_RE)?.[0] ??
    undefined;

  const asinEl = doc.querySelector(selectors.asin);
  const asin = asinEl?.getAttribute("href")?.match(ASIN_RE)?.[1] ?? undefined;

  const lang = doc.documentElement.lang || "en";
  const marketEl = doc.querySelector(selectors.market);
  const market = marketEl?.getAttribute("content") || marketEl?.getAttribute("data-marketplace") || "US";

  return {
    message_text,
    order_id,
    asin,
    buyer_lang: lang,
    market,
  };
}

export function hasMessageNode(doc: Document, selectors = SELECTORS): boolean {
  return !!doc.querySelector(selectors.message);
}

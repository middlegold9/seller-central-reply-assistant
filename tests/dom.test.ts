import { describe, it, expect } from "vitest";
import { parseContext, hasMessageNode } from "../src/lib/dom";

function makeDoc(html: string): Document {
  const d = document.implementation.createHTMLDocument("test");
  d.body.innerHTML = html;
  return d;
}

describe("parseContext", () => {
  it("parses message, order id, asin, lang", () => {
    const doc = makeDoc(`
      <html lang="en"><body>
        <div class="message-thread__message">Where is my order?</div>
        <a href="https://sellercentral.amazon.com/orders/123-4567890-1234567">order</a>
        <a href="https://www.amazon.com/dp/B0ABCDEFGH">product</a>
      </body></html>
    `);
    const ctx = parseContext(doc);
    expect(ctx.message_text).toBe("Where is my order?");
    expect(ctx.order_id).toBe("123-4567890-1234567");
    expect(ctx.asin).toBe("B0ABCDEFGH");
    expect(ctx.buyer_lang).toBe("en");
  });

  it("returns empty message flag when no message node", () => {
    const doc = makeDoc(`<html lang="zh"><body><p>其他页面</p></body></html>`);
    expect(hasMessageNode(doc)).toBe(false);
  });

  it("falls back to text order id when only text present", () => {
    const doc = makeDoc(`
      <div class="message-thread__message">hi</div>
      <span class="order-id">Order: 111-2223334-5556667</span>
    `);
    expect(parseContext(doc).order_id).toBe("111-2223334-5556667");
  });
});

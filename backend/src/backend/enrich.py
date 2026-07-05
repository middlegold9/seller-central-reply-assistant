"""上下文丰富：经 sp-api-mcp-server 取订单/物流实时状态（FR7）。

默认实现把请求转发到 MCP HTTP/SSE 服务端点的 tools/call；测试可注入假客户端。
"""

from __future__ import annotations

from typing import Callable, Optional

import httpx


class EnrichmentClient:
    def __init__(self, base_url: str = "", token: str = "", client: Optional[httpx.Client] = None):
        self.base_url = base_url
        self.token = token
        self._client = client or httpx.Client(timeout=30)

    def get_order(self, order_id: str) -> dict:
        """调用 MCP `spapi_orders_get` + `spapi_orders_buyer_info`(RDT)。"""
        resp = self._client.post(
            f"{self.base_url}/tools/call",
            headers={"Authorization": f"Bearer {self.token}"} if self.token else {},
            json={"name": "spapi_orders_get", "arguments": {"order_id": order_id}},
        )
        resp.raise_for_status()
        return resp.json()


# 可注入的假客户端类型：Callable[[str], dict]
FakeEnricher = Callable[[str], dict]


def enrich_context(context, enricher: Optional[EnrichmentClient] = None,
                   fake: Optional[FakeEnricher] = None):
    """返回 (order_status, ship_status) 或 None。"""
    if not context.order_id:
        return None, None
    if fake is not None:
        data = fake(context.order_id)
    elif enricher is not None:
        data = enricher.get_order(context.order_id)
    else:
        return None, None
    return data.get("order_status"), data.get("ship_status")

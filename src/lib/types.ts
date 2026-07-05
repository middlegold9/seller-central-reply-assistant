// 与后端 backend/types.py 对齐的 TS 类型
export type RiskLevel = "block" | "warn" | "info";
export type Category =
  | "logistics"
  | "quality"
  | "refund"
  | "feedback_removal"
  | "a_to_z"
  | "other";

export interface Context {
  message_text: string;
  market?: string;
  buyer_lang?: string;
  order_id?: string;
  asin?: string;
}

export interface RiskFlag {
  level: RiskLevel;
  rule: string;
  detail: string;
}

export interface Draft {
  draft: string;
  language: string;
  suggested_actions: string[];
  risk_flags: RiskFlag[];
  confidence: number;
  blocked: boolean;
  needs_human: boolean;
  category?: Category;
  order_status?: string;
  ship_status?: string;
}

export interface Settings {
  brand_name: string;
  tone: string;
  refund_limit: number;
  guardrail_strictness: string;
  backend_url: string;
}

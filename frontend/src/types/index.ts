// These types mirror the backend's Pydantic schemas (backend/app/schemas/).
// Keep them in sync manually for now; consider generating them from the
// FastAPI OpenAPI spec (openapi-typescript) once the API surface stabilizes.

export type TransactionTag = "good" | "bad" | "neutral" | "unreviewed";

export interface Goal {
  id: string;
  title: string;
  target_amount: string; // Decimal serializes as string over JSON
  target_date: string; // ISO date
  created_at: string;
}

export interface GoalProgress {
  goal_id: string;
  saved_so_far: string;
  percent_complete: number;
  days_remaining: number;
  required_monthly_savings: string;
}

export interface Transaction {
  id: string;
  amount: string;
  merchant: string | null;
  note: string | null;
  occurred_at: string;
  category_id: string | null;
  tag: TransactionTag;
  created_at: string;
}

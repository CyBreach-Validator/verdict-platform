import api from "./api";

export interface RevalidationHistoryItem {
  id: number;
  verdict_id: number;
  related_verdict_id: number | null;
  rule_id: number;
  rule_name: string;
  old_verdict: string;
  new_verdict: string;
  delta: number;
  improved: boolean;
  gap_closed: boolean;
  verdict_hash: string;
  created_at: string;
}

export interface RevalidationDashboardResponse {
  total_revalidations: number;
  improved: number;
  gap_closed: number;
  history: RevalidationHistoryItem[];
}

export async function getRevalidationDashboard(): Promise<RevalidationDashboardResponse> {
  const response = await api.get("/dashboard/revalidation");

  return response.data;
}
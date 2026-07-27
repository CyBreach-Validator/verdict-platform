import api from "./api";

export type VerdictDetails = {
  id: number;
  rule_id: number;
  rule_name: string;
  verdict: string;
  event_data: string;
  verdict_hash: string;
  is_superseded: boolean;
  superseded_by: number | null;
  created_at: string;
};

export async function getVerdict(
  id: number
): Promise<VerdictDetails> {

  console.log("getVerdict() called with ID:", id);

  const response = await api.get(`/verdicts/${id}`);

  console.log("Verdict response:", response.data);

  return response.data;
}
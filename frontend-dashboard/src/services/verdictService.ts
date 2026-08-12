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

export type RevalidationResponse = {
  old_verdict: {
    id: number;
    verdict: string;
    verdict_hash: string;
    created_at: string;
  };

  new_verdict: {
    id: number;
    verdict: string;
    verdict_hash: string;
    created_at: string;
  };

  rule: {
    id: number;
    name: string;
  };

  validation: {
    status: string;
    [key: string]: unknown;
  };

  comparison: {
    old_score: number;
    new_score: number;
    delta: number;
    improved: boolean;
    gap_closed: boolean;
  };
};

export async function getVerdict(
  id: number
): Promise<VerdictDetails> {
  console.log("getVerdict() called with ID:", id);

  const response = await api.get(`/verdicts/${id}`);

  console.log("Verdict response:", response.data);

  return response.data;
}

export async function revalidateVerdict(
  id: number
): Promise<RevalidationResponse> {
  console.log("revalidateVerdict() called with ID:", id);

  const response = await api.post(
    `/verdicts/${id}/revalidate`
  );

  console.log(
    "Re-validation response:",
    response.data
  );

  return response.data;
}
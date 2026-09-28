import api from "./api";

// Mirrors `app/schemas/verdict.py` (VerdictResponse) and the v2.0 wire contract.
export type VerdictDetails = {
  id: number;
  // B6: `rule_id` is the canonical 64-character content hash shared across
  // pods, not an integer. Typing it as `number` here is what let the mismatch
  // between pods' identifiers go unnoticed on the client.
  action_id: string;
  rule_id: string;
  rule_name: string;
  verdict: string;
  // 0.0-1.0.
  confidence: number;
  causal_chain: string[];
  mttd_seconds: number | null;
  matched_evidence_ref: string | null;
  regulatory_control_refs: string[];
  event_data: string;
  // M12: the contract field is `content_hash`.
  content_hash: string;
  is_superseded: boolean;
  superseded_by: number | null;
  created_at: string;
};

// `POST /verdicts/{id}/revalidate` returns a before/after summary of the two
// rows. It used to be typed as a shape the endpoint never produced, so the
// dashboard's comparison panel read `undefined` off every field.
export type RevalidationVerdict = {
  id: number;
  verdict: string;
  confidence: number;
  content_hash: string;
  created_at: string;
};

export type RevalidationResponse = {
  verdict_id: number;
  previous_verdict_id: number;
  old_verdict: RevalidationVerdict;
  new_verdict: RevalidationVerdict;
  gap_closed: boolean;
  content_hash: string;
  comparison: {
    old_confidence: number;
    new_confidence: number;
    delta: number;
    improved: boolean;
    gap_closed: boolean;
  };
  validation: {
    status: string;
    matched_fields: string[];
  };
};

export async function getVerdict(
  id: number
): Promise<VerdictDetails> {
  const response = await api.get(`/verdicts/${id}`);

  return response.data;
}

export async function revalidateVerdict(
  id: number
): Promise<RevalidationResponse> {
  const response = await api.post(
    `/verdicts/${id}/revalidate`
  );

  return response.data;
}

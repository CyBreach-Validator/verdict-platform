import api from "./api";

export interface CausalChain {
  rule: {
    id: number;
    name: string;
    technique: string | null;
  };

  event: Record<string, unknown>;

  validation: {
    status: string;
  };

  classifier: {
    status: string;
  };

  verdict: {
    id: number;
    hash: string;
    superseded: boolean;
  };
}

export const getCausalChain = async (
  verdictId: number
): Promise<CausalChain> => {
  const response = await api.get(
    `/verdicts/${verdictId}/chain`
  );

  return response.data;
};
import api from "./api";

export interface CoverageItem {
  technique: string;
  name: string;
  tactic: string;
  rule_name: string;
  status: string;
}

export const getDetectionCoverage = async (): Promise<CoverageItem[]> => {
  const response = await api.get("/dashboard/coverage");
  return response.data;
};
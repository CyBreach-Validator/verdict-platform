import axios from "axios";

const API_URL = "http://127.0.0.1:8033";

const getAuthHeaders = () => {
  const token = localStorage.getItem("access_token");

  return {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  };
};

export interface RuleComparison {
  current: {
    title: string;
    query: string;
    severity: string;
    status: string;
  };
  proposed: {
    title: string;
    query: string;
    severity: string;
    status: string;
  };
}

export const getRuleComparison = async (
  ruleId: number
): Promise<RuleComparison> => {
  const response = await axios.get(
    `${API_URL}/rules/${ruleId}/compare`,
    getAuthHeaders()
  );

  return response.data;
};
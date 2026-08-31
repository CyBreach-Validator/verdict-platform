import api from "./api";

export interface Rule {
  id: number;
  rule_name: string;
  rule_type: string;
  severity: string;
  description?: string | null;
  query: string;
  status: string;
  mitre_technique?: string | null;
}

export interface RuleInput {
  rule_name: string;
  rule_type: string;
  severity: string;
  description?: string;
  query: string;
  status: string;
  mitre_technique?: string;
}

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

export const getRules = async (): Promise<Rule[]> => {
  const response = await api.get("/rules");
  return response.data;
};

export const searchRules = async (
  query: string
): Promise<Rule[]> => {
  const response = await api.get(
    `/rules/search?q=${encodeURIComponent(query)}`
  );

  return response.data;
};

export const getRule = async (
  ruleId: number
): Promise<Rule> => {
  const response = await api.get(`/rules/${ruleId}`);
  return response.data;
};

export const createRule = async (
  rule: RuleInput
): Promise<Rule> => {
  const response = await api.post("/rules", rule);
  return response.data;
};

export const updateRule = async (
  ruleId: number,
  rule: RuleInput
): Promise<Rule> => {
  const response = await api.put(`/rules/${ruleId}`, rule);
  return response.data;
};

export const deleteRule = async (
  ruleId: number
): Promise<void> => {
  await api.delete(`/rules/${ruleId}`);
};

export const approveRule = async (
  ruleId: number
): Promise<Rule> => {
  const response = await api.put(
    `/rules/${ruleId}/approve`,
    {}
  );

  return response.data;
};

export const getRuleComparison = async (
  ruleId: number
): Promise<RuleComparison> => {
  const response = await api.get(
    `/rules/${ruleId}/compare`
  );

  return response.data;
};
import api from "./api";

export interface Rule {
  id: number;
  rule_name: string;
  rule_type: string;
  severity: string;
  description?: string;
  query: string;
  status: string;
  mitre_technique?: string;
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

// Get/search rules
export const searchRules = async (
  search = ""
): Promise<Rule[]> => {
  const response = await api.get(
    `/rules/search?q=${encodeURIComponent(search)}`
  );

  return response.data;
};

// Alias for compatibility
export const getRules = async (
  search = ""
): Promise<Rule[]> => {
  return searchRules(search);
};

// Create rule
export const createRule = async (
  rule: RuleInput
): Promise<Rule> => {
  const response = await api.post("/rules", rule);

  return response.data;
};

// Update rule
export const updateRule = async (
  ruleId: number,
  rule: RuleInput
): Promise<Rule> => {
  const response = await api.put(
    `/rules/${ruleId}`,
    rule
  );

  return response.data;
};

// Delete rule
export const deleteRule = async (
  ruleId: number
): Promise<void> => {
  await api.delete(`/rules/${ruleId}`);
};

// Submit rule for approval
export const submitRule = async (
  ruleId: number
): Promise<Rule> => {
  const response = await api.put(
    `/rules/${ruleId}/submit`,
    {}
  );

  return response.data;
};

// Approve rule
export const approveRule = async (
  ruleId: number
): Promise<Rule> => {
  const response = await api.put(
    `/rules/${ruleId}/approve`,
    {}
  );

  return response.data;
};

// Reject rule
export const rejectRule = async (
  ruleId: number
): Promise<Rule> => {
  const response = await api.put(
    `/rules/${ruleId}/reject`,
    {}
  );

  return response.data;
};

// Compare current and proposed rule
export const getRuleComparison = async (
  ruleId: number
): Promise<RuleComparison> => {
  const response = await api.get(
    `/rules/${ruleId}/compare`
  );

  return response.data;
};

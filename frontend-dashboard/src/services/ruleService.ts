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

export interface RuleComparisonBlock {
  title: string;
  query: string;
  severity: string;
  status: string;
}

export interface RuleComparison {
  current: RuleComparisonBlock;
  proposed: RuleComparisonBlock | null;
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

// Compare current rule against a proposed revision.
//
// N-D19: this used to be a GET and the backend answered with a hardcoded
// "Suspicious PowerShell" block, so the diff shown here was always between a
// real rule and a fabricated one. It is now a POST carrying the proposal, and
// `proposed` is null when no proposal has been submitted.
export const getRuleComparison = async (
  ruleId: number,
  proposed?: Partial<RuleComparisonBlock>
): Promise<RuleComparison> => {
  const response = await api.post(
    `/rules/${ruleId}/compare`,
    proposed ?? {}
  );

  return response.data;
};

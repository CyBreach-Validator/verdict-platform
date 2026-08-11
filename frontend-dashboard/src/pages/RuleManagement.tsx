import { useEffect, useState } from "react";
import api from "../services/api";
import RuleComparison from "../components/rules/RuleComparison";

interface Rule {
  id: number;
  rule_name: string;
  rule_type: string;
  severity: string;
  status: string;
}

export default function RuleManagement() {
  const [rules, setRules] = useState<Rule[]>([]);
  const [search, setSearch] = useState("");
  const [selectedRuleId, setSelectedRuleId] = useState<number | null>(null);

  const token = localStorage.getItem("access_token");

  console.log("Token from localStorage:", token);

  const fetchRules = async () => {
    try {
      console.log("Fetching rules...");

      const response = await api.get(
        `/rules/search?q=${encodeURIComponent(search)}`
      );

      console.log("Rules response:", response.data);

      setRules(response.data);
    } catch (err: any) {
      console.error("Failed to fetch rules");
      console.error("Status:", err.response?.status);
      console.error("Response:", err.response?.data);
    }
  };

  const approveRule = async (id: number) => {
    try {
      console.log("Approving rule:", id);

      await api.put(`/rules/${id}/approve`, {});

      console.log("Rule approved successfully");

      fetchRules();
    } catch (err: any) {
      console.error("Failed to approve rule");
      console.error("Status:", err.response?.status);
      console.error("Response:", err.response?.data);
    }
  };

  useEffect(() => {
    fetchRules();
  }, []);

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-5">
        Rule Management
      </h2>

      <input
        type="text"
        placeholder="Search rules..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="border rounded p-2 mb-5 w-full"
      />

      <button
        onClick={fetchRules}
        className="bg-blue-600 text-white px-4 py-2 rounded mb-5"
      >
        Search
      </button>

      <table className="w-full border">
        <thead className="bg-gray-100">
          <tr>
            <th className="border p-2">Rule</th>
            <th className="border p-2">Type</th>
            <th className="border p-2">Severity</th>
            <th className="border p-2">Status</th>
            <th className="border p-2">Action</th>
          </tr>
        </thead>

        <tbody>
          {rules.map((rule) => (
            <tr key={rule.id}>
              <td className="border p-2">
                {rule.rule_name}
              </td>

              <td className="border p-2">
                {rule.rule_type}
              </td>

              <td className="border p-2">
                {rule.severity}
              </td>

              <td className="border p-2">
                {rule.status}
              </td>

              <td className="border p-2">
                <div className="flex gap-2">
                  <button
                    className="bg-blue-600 text-white px-3 py-1 rounded"
                    onClick={() => {
                      console.log("Compare clicked:", rule.id);
                      setSelectedRuleId(rule.id);
                    }}
                  >
                    Compare
                  </button>

                  {rule.status === "Pending" ? (
                    <button
                      className="bg-green-600 text-white px-3 py-1 rounded"
                      onClick={() => approveRule(rule.id)}
                    >
                      Approve
                    </button>
                  ) : (
                    <span>-</span>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {selectedRuleId && (
        <RuleComparison ruleId={selectedRuleId} />
      )}
    </div>
  );
}
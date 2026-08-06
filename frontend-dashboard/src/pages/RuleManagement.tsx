import { useEffect, useState } from "react";
import axios from "axios";
import RuleComparison from "../components/rules/RuleComparison";

interface Rule {
  id: number;
  rule_name: string;
  rule_type: string;
  severity: string;
  status: string;
}

const API_URL = "http://127.0.0.1:8033";

export default function RuleManagement() {
  const [rules, setRules] = useState<Rule[]>([]);
  const [search, setSearch] = useState("");

  const [selectedRuleId, setSelectedRuleId] = useState<number | null>(null);

  const token = localStorage.getItem("access_token");
  console.log("Token from localStorage:", token);

  const fetchRules = async () => {
  try {
    console.log("Token:", token);

    const config = {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    };

    console.log("Request Config:", config);

    const response = await axios.get(
      `${API_URL}/rules/search?q=${search}`,
      config
    );

    console.log("Response:", response.data);

    setRules(response.data);
  } catch (err: any) {
    console.log("Status:", err.response?.status);
    console.log("Response:", err.response?.data);
    console.log("Headers Sent:", err.config?.headers);
  }
};

  const approveRule = async (id: number) => {
    try {
      await axios.put(
        `${API_URL}/rules/${id}/approve`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      fetchRules();
    } catch (err) {
      console.error(err);
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
              <td className="border p-2">{rule.rule_name}</td>
              <td className="border p-2">{rule.rule_type}</td>
              <td className="border p-2">{rule.severity}</td>

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
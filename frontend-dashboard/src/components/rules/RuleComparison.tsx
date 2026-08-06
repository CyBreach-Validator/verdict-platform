import { useEffect, useState } from "react";
import { getRuleComparison } from "../../services/ruleService";
import type { RuleComparison as RuleComparisonType } from "../../services/ruleService";

interface Props {
  ruleId: number;
}

export default function RuleComparison({ ruleId }: Props) {
  const [comparison, setComparison] = useState<RuleComparisonType | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadComparison = async () => {
      try {
        const data = await getRuleComparison(ruleId);
        setComparison(data);
      } catch (error) {
        console.error("Failed to load rule comparison:", error);
      } finally {
        setLoading(false);
      }
    };

    loadComparison();
  }, [ruleId]);

  if (loading) {
    return <p>Loading comparison...</p>;
  }

  if (!comparison) {
    return <p>No comparison data found.</p>;
  }

  const renderRow = (
    label: string,
    current: string,
    proposed: string
  ) => {
    const changed = current !== proposed;

    return (
      <tr key={label}>
        <td className="border px-4 py-2 font-medium">{label}</td>

        <td
          className={`border px-4 py-2 ${
            changed ? "bg-red-100" : "bg-green-100"
          }`}
        >
          {current}
        </td>

        <td
          className={`border px-4 py-2 ${
            changed ? "bg-yellow-100" : "bg-green-100"
          }`}
        >
          {proposed}
        </td>
      </tr>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow p-6 mt-6">
      <h2 className="text-xl font-bold mb-4">Rule Comparison</h2>

      <table className="w-full border-collapse border">
        <thead>
          <tr className="bg-gray-200">
            <th className="border px-4 py-2">Field</th>
            <th className="border px-4 py-2">Current Rule</th>
            <th className="border px-4 py-2">Proposed Rule</th>
          </tr>
        </thead>

        <tbody>
          {renderRow(
            "Title",
            comparison.current.title,
            comparison.proposed.title
          )}

          {renderRow(
            "Query",
            comparison.current.query,
            comparison.proposed.query
          )}

          {renderRow(
            "Severity",
            comparison.current.severity,
            comparison.proposed.severity
          )}

          {renderRow(
            "Status",
            comparison.current.status,
            comparison.proposed.status
          )}
        </tbody>
      </table>
    </div>
  );
}
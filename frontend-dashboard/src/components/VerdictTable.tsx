import { useNavigate } from "react-router-dom";
import StatusBadge from "./StatusBadge";

interface Verdict {
  id: number;
  rule_name: string;
  verdict: string;
  created_at: string;
}

interface VerdictTableProps {
  verdicts: Verdict[];
}

function VerdictTable({ verdicts }: VerdictTableProps) {
  const navigate = useNavigate();

  return (
    <div className="responsive-table-container w-full min-w-0 overflow-x-auto">
      <table className="verdict-table w-full min-w-[760px] border-collapse">
        <thead>
          <tr>
            <th className="w-[80px] px-4 py-3 text-left">
              ID
            </th>

            <th className="min-w-[280px] px-4 py-3 text-left">
              Rule Name
            </th>

            <th className="w-[150px] px-4 py-3 text-left">
              Verdict
            </th>

            <th className="w-[220px] px-4 py-3 text-left">
              Created At
            </th>
          </tr>
        </thead>

        <tbody>
          {verdicts.map((verdict) => (
            <tr
              key={verdict.id}
              onClick={() =>
                navigate(`/verdicts/${verdict.id}`)
              }
              className="cursor-pointer transition hover:bg-gray-50"
            >
              <td className="px-4 py-3 align-middle font-medium">
                {verdict.id}
              </td>

              <td className="min-w-0 px-4 py-3 align-middle">
                <div className="break-words">
                  {verdict.rule_name}
                </div>
              </td>

              <td className="px-4 py-3 align-middle">
                <div className="flex items-center">
                  <StatusBadge
                    verdict={verdict.verdict}
                  />
                </div>
              </td>

              <td className="px-4 py-3 align-middle whitespace-nowrap">
                {new Date(
                  verdict.created_at
                ).toLocaleString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default VerdictTable;
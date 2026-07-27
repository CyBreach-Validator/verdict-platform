import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { getVerdict } from "../services/verdictService";
import type { VerdictDetails } from "../services/verdictService";
import CausalChain from "../components/verdicts/CausalChain";

export default function VerdictDetailsPage() {
  const { id } = useParams();

  const [verdict, setVerdict] =
    useState<VerdictDetails | null>(null);

  const [loading, setLoading] = useState(true);

  useEffect(() => {
     console.log("VerdictDetails mounted");
     console.log("Route ID:", id);
    
     if (!id) return;

    getVerdict(Number(id))
      .then((data) => {
        setVerdict(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, [id]);

  if (loading) {
    return <h2>Loading...</h2>;
  }

  if (!verdict) {
    return <h2>Verdict not found.</h2>;
  }

  return (
    <div style={{ padding: 30 }}>

      <Link to="/dashboard">
        ← Back to Dashboard
      </Link>

      <h1 style={{ marginTop: 20 }}>
        Verdict Details
      </h1>

      <table
        style={{
          borderCollapse: "collapse",
          width: "100%",
          marginTop: 20,
        }}
      >
        <tbody>
          <tr>
            <td><b>ID</b></td>
            <td>{verdict.id}</td>
          </tr>

          <tr>
            <td><b>Rule Name</b></td>
            <td>{verdict.rule_name}</td>
          </tr>

          <tr>
            <td><b>Rule ID</b></td>
            <td>{verdict.rule_id}</td>
          </tr>

          <tr>
            <td><b>Verdict</b></td>
            <td>{verdict.verdict}</td>
          </tr>

          <tr>
            <td><b>Verdict Hash</b></td>
            <td
              style={{
                wordBreak: "break-all",
              }}
            >
              {verdict.verdict_hash}
            </td>
          </tr>

          <tr>
            <td><b>Superseded</b></td>
            <td>
              {verdict.is_superseded ? "Yes" : "No"}
            </td>
          </tr>

          <tr>
            <td><b>Superseded By</b></td>
            <td>
              {verdict.superseded_by ?? "-"}
            </td>
          </tr>

          <tr>
            <td><b>Created At</b></td>
            <td>
              {new Date(
                verdict.created_at
              ).toLocaleString()}
            </td>
          </tr>
        </tbody>
      </table>

      <h2 style={{ marginTop: 30 }}>
        Event Data
      </h2>

      <pre
        style={{
          background: "#f5f5f5",
          padding: 20,
          borderRadius: 8,
        }}
      >
        {JSON.stringify(
          JSON.parse(verdict.event_data),
          null,
          2
        )}
      </pre>
      <CausalChain verdictId={verdict.id} />
    </div>
  );
}
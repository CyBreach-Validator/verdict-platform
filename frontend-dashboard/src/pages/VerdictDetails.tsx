import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import {
  getVerdict,
  revalidateVerdict,
} from "../services/verdictService";

import type {
  VerdictDetails,
  RevalidationResponse,
} from "../services/verdictService";

import CausalChain from "../components/verdicts/CausalChain";
import VerdictTimeline from "../components/verdicts/VerdictTimeline";

export default function VerdictDetailsPage() {
  const { id } = useParams();

  const [verdict, setVerdict] =
    useState<VerdictDetails | null>(null);

  const [loading, setLoading] = useState(true);

  const [revalidating, setRevalidating] =
    useState(false);

  const [revalidationResult, setRevalidationResult] =
    useState<RevalidationResponse | null>(null);

  const [revalidationError, setRevalidationError] =
    useState<string | null>(null);

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

  const handleRevalidate = async () => {
    if (!verdict) return;

    setRevalidating(true);
    setRevalidationError(null);
    setRevalidationResult(null);

    try {
      const result = await revalidateVerdict(verdict.id);

      console.log(
        "Re-validation completed:",
        result
      );

      setRevalidationResult(result);

      // Refresh the original verdict so that
      // superseded/superseded_by information is updated.
      const updatedVerdict = await getVerdict(
        verdict.id
      );

      setVerdict(updatedVerdict);
    } catch (err) {
      console.error(
        "Re-validation failed:",
        err
      );

      setRevalidationError(
        "Re-validation failed. Please try again."
      );
    } finally {
      setRevalidating(false);
    }
  };

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
              {verdict.is_superseded
                ? "Yes"
                : "No"}
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

      {/* Re-Validation */}
      <div style={{ marginTop: 30 }}>
        <button
           onClick={handleRevalidate}
           disabled={revalidating}
           style={{
             padding: "10px 18px",
             borderRadius: 6,
             border: "1px solid #333",
             background: revalidating ? "#ddd" : "#333",
             color: revalidating ? "#666" : "#fff",
             cursor: revalidating
               ? "not-allowed"
               : "pointer",
             fontWeight: "bold",
             fontSize: 14,
           }}
         >
           {revalidating
             ? "Re-validating..."
             : "Re-Validate"}
         </button>
      </div>

      {revalidationError && (
        <div
          style={{
            marginTop: 15,
            padding: 12,
            borderRadius: 6,
            background: "#ffe6e6",
            color: "#b00020",
          }}
        >
          {revalidationError}
        </div>
      )}

      {/* Re-Validation Comparison */}
      {revalidationResult && (
        <div
          style={{
            marginTop: 30,
            padding: 20,
            border: "1px solid #ddd",
            borderRadius: 8,
          }}
        >
          <h2>
            Re-Validation Result
          </h2>

          <table
            style={{
              borderCollapse: "collapse",
              width: "100%",
              marginTop: 15,
            }}
          >
            <tbody>
              <tr>
                <td><b>Original Verdict</b></td>
                <td>
                  {
                    revalidationResult
                      .old_verdict.verdict
                  }
                </td>
              </tr>

              <tr>
                <td><b>New Verdict</b></td>
                <td>
                  {
                    revalidationResult
                      .new_verdict.verdict
                  }
                </td>
              </tr>

              <tr>
                <td><b>Original Score</b></td>
                <td>
                  {
                    revalidationResult
                      .comparison.old_score
                  }
                </td>
              </tr>

              <tr>
                <td><b>New Score</b></td>
                <td>
                  {
                    revalidationResult
                      .comparison.new_score
                  }
                </td>
              </tr>

              <tr>
                <td><b>Score Delta</b></td>
                <td>
                  {
                    revalidationResult
                      .comparison.delta > 0
                      ? `+${revalidationResult.comparison.delta}`
                      : revalidationResult.comparison.delta
                  }
                </td>
              </tr>

              <tr>
                <td><b>Improved</b></td>
                <td>
                  {
                    revalidationResult
                      .comparison.improved
                      ? "Yes"
                      : "No"
                  }
                </td>
              </tr>

              <tr>
                <td><b>Gap Closed</b></td>
                <td>
                  {
                    revalidationResult
                      .comparison.gap_closed
                      ? "Yes"
                      : "No"
                  }
                </td>
              </tr>

              <tr>
                <td><b>New Verdict ID</b></td>
                <td>
                  {
                    revalidationResult
                      .new_verdict.id
                  }
                </td>
              </tr>

              <tr>
                <td><b>New Verdict Hash</b></td>
                <td
                  style={{
                    wordBreak: "break-all",
                  }}
                >
                  {
                    revalidationResult
                      .new_verdict.verdict_hash
                  }
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      )}

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

      <VerdictTimeline
        verdict={verdict}
        revalidationResult={revalidationResult}
      />

      <CausalChain verdictId={verdict.id} />
    </div>
  );
}
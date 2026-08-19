import type {
  VerdictDetails,
  RevalidationResponse,
} from "../../services/verdictService";

interface VerdictTimelineProps {
  verdict: VerdictDetails;
  revalidationResult?: RevalidationResponse | null;
}

function getVerdictStyle(verdict: string) {
  switch (verdict.toLowerCase()) {
    case "detected":
      return {
        background: "#e6f7e6",
        border: "#2e7d32",
        color: "#2e7d32",
      };

    case "missed":
      return {
        background: "#ffe6e6",
        border: "#c62828",
        color: "#c62828",
      };

    case "partial":
      return {
        background: "#fff4cc",
        border: "#f9a825",
        color: "#8a6d00",
      };

    case "no data":
      return {
        background: "#eeeeee",
        border: "#757575",
        color: "#555",
      };

    default:
      return {
        background: "#f5f5f5",
        border: "#777",
        color: "#333",
      };
  }
}

function TimelineNode({
  title,
  verdict,
  id,
  hash,
  createdAt,
  description,
}: {
  title: string;
  verdict: string;
  id: number;
  hash: string;
  createdAt: string;
  description: string;
}) {
  const style = getVerdictStyle(verdict);

  return (
    <div
      style={{
        display: "flex",
        gap: 16,
        marginBottom: 30,
      }}
    >
      {/* Timeline marker */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
        }}
      >
        <div
          style={{
            width: 18,
            height: 18,
            borderRadius: "50%",
            background: style.border,
            border: `3px solid ${style.background}`,
            boxShadow: `0 0 0 2px ${style.border}`,
            flexShrink: 0,
          }}
        />

        <div
          style={{
            width: 2,
            flex: 1,
            background: "#ddd",
            marginTop: 5,
          }}
        />
      </div>

      {/* Timeline content */}
      <div
        style={{
          flex: 1,
          padding: 18,
          border: "1px solid #ddd",
          borderRadius: 10,
          background: "#fff",
          boxShadow: "0 2px 6px rgba(0,0,0,0.05)",
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: 10,
          }}
        >
          <h3 style={{ margin: 0 }}>{title}</h3>

          <span
            style={{
              display: "inline-block",
              padding: "5px 12px",
              borderRadius: 20,
              background: style.background,
              border: `1px solid ${style.border}`,
              color: style.color,
              fontWeight: "bold",
              fontSize: 13,
            }}
          >
            {verdict}
          </span>
        </div>

        <p
          style={{
            marginTop: 8,
            marginBottom: 15,
            color: "#666",
          }}
        >
          {description}
        </p>

        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              "repeat(auto-fit, minmax(220px, 1fr))",
            gap: 12,
          }}
        >
          <div>
            <strong>Verdict ID</strong>
            <div>{id}</div>
          </div>

          <div>
            <strong>Created At</strong>
            <div>
              {new Date(createdAt).toLocaleString()}
            </div>
          </div>

          <div style={{ gridColumn: "1 / -1" }}>
            <strong>Verdict Hash</strong>
            <div
              style={{
                marginTop: 4,
                wordBreak: "break-all",
                fontFamily: "monospace",
                fontSize: 12,
                color: "#555",
              }}
            >
              {hash}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function VerdictTimeline({
  verdict,
  revalidationResult,
}: VerdictTimelineProps) {
  return (
    <div
      style={{
        marginTop: 35,
        padding: 20,
        border: "1px solid #ddd",
        borderRadius: 10,
        background: "#fafafa",
      }}
    >
      <h2 style={{ marginTop: 0 }}>
        Verdict Timeline
      </h2>

      <p style={{ color: "#666" }}>
        History of the verdict and its re-validation lifecycle.
      </p>

      {/* Original Verdict */}
      <TimelineNode
        title="Original Verdict"
        verdict={verdict.verdict}
        id={verdict.id}
        hash={verdict.verdict_hash}
        createdAt={verdict.created_at}
        description={
          verdict.is_superseded
            ? "This verdict was superseded by a later re-validation result."
            : "This is the current verdict for the selected validation."
        }
      />

      {/* Re-validation */}
      {revalidationResult && (
        <>
          <div
            style={{
              marginLeft: 34,
              marginBottom: 25,
              padding: 15,
              borderRadius: 8,
              border: "1px dashed #aaa",
              background: "#f8f8f8",
            }}
          >
            <strong>Re-validation Event</strong>

            <div
              style={{
                marginTop: 10,
                display: "grid",
                gridTemplateColumns:
                  "repeat(auto-fit, minmax(150px, 1fr))",
                gap: 10,
              }}
            >
              <div>
                <strong>Score</strong>
                <div>
                  {revalidationResult.comparison.old_score}
                  {" → "}
                  {revalidationResult.comparison.new_score}
                </div>
              </div>

              <div>
                <strong>Delta</strong>
                <div>
                  {revalidationResult.comparison.delta > 0
                    ? `+${revalidationResult.comparison.delta}`
                    : revalidationResult.comparison.delta}
                </div>
              </div>

              <div>
                <strong>Improved</strong>
                <div>
                  {revalidationResult.comparison.improved
                    ? "Yes"
                    : "No"}
                </div>
              </div>

              <div>
                <strong>Gap Closed</strong>
                <div>
                  {revalidationResult.comparison.gap_closed
                    ? "Yes"
                    : "No"}
                </div>
              </div>
            </div>
          </div>

          {/* New Verdict */}
          <TimelineNode
            title="New Verdict"
            verdict={revalidationResult.new_verdict.verdict}
            id={revalidationResult.new_verdict.id}
            hash={revalidationResult.new_verdict.verdict_hash}
            createdAt={revalidationResult.new_verdict.created_at}
            description="Verdict generated after re-validation."
          />
        </>
      )}

      {!revalidationResult && (
        <div
          style={{
            marginLeft: 34,
            padding: 15,
            borderRadius: 8,
            background: "#f5f5f5",
            border: "1px dashed #bbb",
            color: "#666",
          }}
        >
          No re-validation event is available for this
          verdict yet.
        </div>
      )}
    </div>
  );
}
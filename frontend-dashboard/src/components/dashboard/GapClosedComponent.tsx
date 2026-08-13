import type {
  RevalidationHistoryItem,
} from "../../services/revalidationDashboardService";

interface GapClosedComponentProps {
  history: RevalidationHistoryItem[];
}

export default function GapClosedComponent({
  history,
}: GapClosedComponentProps) {
  const closedGaps = history.filter(
    (item) => item.gap_closed
  );

  return (
    <div
      style={{
        marginTop: 40,
        padding: 24,
        border: "1px solid #ddd",
        borderRadius: 8,
      }}
    >
      <h2>Gap-Closed Summary</h2>

      <div
        style={{
          marginTop: 20,
          padding: 20,
          border: "1px solid #ddd",
          borderRadius: 8,
        }}
      >
        <h3>Gaps Closed</h3>

        <p
          style={{
            fontSize: 32,
            fontWeight: "bold",
            margin: "10px 0",
          }}
        >
          {closedGaps.length}
        </p>
      </div>

      <div style={{ marginTop: 30 }}>
        <h3>Closed Detection Gaps</h3>

        {closedGaps.length === 0 ? (
          <p>
            No detection gaps have been closed yet.
          </p>
        ) : (
          <div
            style={{
              overflowX: "auto",
              marginTop: 15,
            }}
          >
            <table
              style={{
                borderCollapse: "collapse",
                width: "100%",
              }}
            >
              <thead>
                <tr>
                  <th
                    style={{
                      border: "1px solid #ddd",
                      padding: 10,
                      textAlign: "left",
                    }}
                  >
                    Rule
                  </th>

                  <th
                    style={{
                      border: "1px solid #ddd",
                      padding: 10,
                      textAlign: "left",
                    }}
                  >
                    Before
                  </th>

                  <th
                    style={{
                      border: "1px solid #ddd",
                      padding: 10,
                      textAlign: "left",
                    }}
                  >
                    After
                  </th>

                  <th
                    style={{
                      border: "1px solid #ddd",
                      padding: 10,
                      textAlign: "left",
                    }}
                  >
                    Delta
                  </th>

                  <th
                    style={{
                      border: "1px solid #ddd",
                      padding: 10,
                      textAlign: "left",
                    }}
                  >
                    Date
                  </th>
                </tr>
              </thead>

              <tbody>
                {closedGaps.map((item) => (
                  <tr key={item.id}>
                    <td
                      style={{
                        border: "1px solid #ddd",
                        padding: 10,
                      }}
                    >
                      {item.rule_name}
                    </td>

                    <td
                      style={{
                        border: "1px solid #ddd",
                        padding: 10,
                      }}
                    >
                      {item.old_verdict}
                    </td>

                    <td
                      style={{
                        border: "1px solid #ddd",
                        padding: 10,
                      }}
                    >
                      {item.new_verdict}
                    </td>

                    <td
                      style={{
                        border: "1px solid #ddd",
                        padding: 10,
                      }}
                    >
                      {item.delta > 0
                        ? `+${item.delta}`
                        : item.delta}
                    </td>

                    <td
                      style={{
                        border: "1px solid #ddd",
                        padding: 10,
                      }}
                    >
                      {new Date(
                        item.created_at
                      ).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
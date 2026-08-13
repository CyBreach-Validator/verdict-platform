import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import GapClosedComponent from "../components/dashboard/GapClosedComponent";

import {
  getRevalidationDashboard,
} from "../services/revalidationDashboardService";

import type {
  RevalidationDashboardResponse,
} from "../services/revalidationDashboardService";

export default function RevalidationDashboard() {
  const [data, setData] =
    useState<RevalidationDashboardResponse | null>(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);

  useEffect(() => {
    getRevalidationDashboard()
      .then((result) => {
        setData(result);
        setLoading(false);
      })
      .catch((err) => {
        console.error(
          "Failed to load re-validation dashboard:",
          err
        );

        setError(
          "Failed to load re-validation dashboard."
        );

        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div style={{ padding: 30 }}>
        <h2>Loading Re-Validation Dashboard...</h2>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: 30 }}>
        <h2>{error}</h2>

        <Link to="/dashboard">
          ← Back to Dashboard
        </Link>
      </div>
    );
  }

  if (!data) {
    return (
      <div style={{ padding: 30 }}>
        <h2>No re-validation data available.</h2>
      </div>
    );
  }

  /*
   * Build cumulative trajectory data.
   *
   * Each history record represents one re-validation.
   * We calculate the running number of improvements
   * and gaps closed so the dashboard can show progress
   * over time.
   */
  let cumulativeImproved = 0;
  let cumulativeGapClosed = 0;

  const trajectory = data.history.map((item, index) => {
    if (item.improved) {
      cumulativeImproved++;
    }

    if (item.gap_closed) {
      cumulativeGapClosed++;
    }

    return {
      ...item,
      sequence: index + 1,
      cumulativeImproved,
      cumulativeGapClosed,
    };
  });

  const maxTrajectoryValue = Math.max(
    data.total_revalidations,
    cumulativeImproved,
    cumulativeGapClosed,
    1
  );

  return (
    <div style={{ padding: 30 }}>
      <Link to="/dashboard">
        ← Back to Dashboard
      </Link>

      <h1 style={{ marginTop: 20 }}>
        Re-Validation Dashboard
      </h1>

      {/* Summary Cards */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns:
            "repeat(3, minmax(200px, 1fr))",
          gap: 20,
          marginTop: 30,
        }}
      >
        <div
          style={{
            padding: 20,
            border: "1px solid #ddd",
            borderRadius: 8,
          }}
        >
          <h3>Total Re-Validations</h3>

          <p
            style={{
              fontSize: 32,
              fontWeight: "bold",
              margin: "10px 0",
            }}
          >
            {data.total_revalidations}
          </p>
        </div>

        <div
          style={{
            padding: 20,
            border: "1px solid #ddd",
            borderRadius: 8,
          }}
        >
          <h3>Improvements</h3>

          <p
            style={{
              fontSize: 32,
              fontWeight: "bold",
              margin: "10px 0",
            }}
          >
            {data.improved}
          </p>
        </div>

        <div
          style={{
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
            {data.gap_closed}
          </p>
        </div>
      </div>

      {/* Improvement Trajectory */}
      
      <GapClosedComponent history={data.history} />
      
      <div
        style={{
          marginTop: 40,
          padding: 20,
          border: "1px solid #ddd",
          borderRadius: 8,
        }}
      >
        <h2>Improvement Trajectory</h2>

        {trajectory.length === 0 ? (
          <p>No trajectory data available.</p>
        ) : (
          <>
            <p
              style={{
                color: "#666",
                marginBottom: 25,
              }}
            >
              Cumulative improvement and gap-closure progress
              across re-validations.
            </p>

            {trajectory.map((item) => (
              <div
                key={item.id}
                style={{
                  marginBottom: 25,
                }}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    marginBottom: 8,
                    fontWeight: "bold",
                  }}
                >
                  <span>
                    Re-Validation #{item.sequence}
                  </span>

                  <span>
                    {new Date(
                      item.created_at
                    ).toLocaleString()}
                  </span>
                </div>

                {/* Total Re-validations */}
                <div style={{ marginBottom: 8 }}>
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      fontSize: 14,
                      marginBottom: 4,
                    }}
                  >
                    <span>Re-validations</span>
                    <span>
                      {item.sequence}
                    </span>
                  </div>

                  <div
                    style={{
                      width: "100%",
                      height: 10,
                      background: "#eee",
                      borderRadius: 5,
                    }}
                  >
                    <div
                      style={{
                        width: `${
                          (item.sequence /
                            maxTrajectoryValue) *
                          100
                        }%`,
                        height: "100%",
                        background: "#555",
                        borderRadius: 5,
                      }}
                    />
                  </div>
                </div>

                {/* Improvements */}
                <div style={{ marginBottom: 8 }}>
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      fontSize: 14,
                      marginBottom: 4,
                    }}
                  >
                    <span>Improvements</span>
                    <span>
                      {item.cumulativeImproved}
                    </span>
                  </div>

                  <div
                    style={{
                      width: "100%",
                      height: 10,
                      background: "#eee",
                      borderRadius: 5,
                    }}
                  >
                    <div
                      style={{
                        width: `${
                          (item.cumulativeImproved /
                            maxTrajectoryValue) *
                          100
                        }%`,
                        height: "100%",
                        background: "#333",
                        borderRadius: 5,
                      }}
                    />
                  </div>
                </div>

                {/* Gaps Closed */}
                <div>
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      fontSize: 14,
                      marginBottom: 4,
                    }}
                  >
                    <span>Gaps Closed</span>
                    <span>
                      {item.cumulativeGapClosed}
                    </span>
                  </div>

                  <div
                    style={{
                      width: "100%",
                      height: 10,
                      background: "#eee",
                      borderRadius: 5,
                    }}
                  >
                    <div
                      style={{
                        width: `${
                          (item.cumulativeGapClosed /
                            maxTrajectoryValue) *
                          100
                        }%`,
                        height: "100%",
                        background: "#777",
                        borderRadius: 5,
                      }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </>
        )}
      </div>

      {/* Re-Validation History */}
      <div style={{ marginTop: 40 }}>
        <h2>Re-Validation History</h2>

        {data.history.length === 0 ? (
          <p>No re-validation history available.</p>
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
                    }}
                  >
                    Rule
                  </th>

                  <th
                    style={{
                      border: "1px solid #ddd",
                      padding: 10,
                    }}
                  >
                    Before
                  </th>

                  <th
                    style={{
                      border: "1px solid #ddd",
                      padding: 10,
                    }}
                  >
                    After
                  </th>

                  <th
                    style={{
                      border: "1px solid #ddd",
                      padding: 10,
                    }}
                  >
                    Delta
                  </th>

                  <th
                    style={{
                      border: "1px solid #ddd",
                      padding: 10,
                    }}
                  >
                    Improved
                  </th>

                  <th
                    style={{
                      border: "1px solid #ddd",
                      padding: 10,
                    }}
                  >
                    Gap Closed
                  </th>

                  <th
                    style={{
                      border: "1px solid #ddd",
                      padding: 10,
                    }}
                  >
                    Date
                  </th>
                </tr>
              </thead>

              <tbody>
                {data.history.map((item) => (
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
                      {item.improved ? "Yes" : "No"}
                    </td>

                    <td
                      style={{
                        border: "1px solid #ddd",
                        padding: 10,
                      }}
                    >
                      {item.gap_closed ? "Yes" : "No"}
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
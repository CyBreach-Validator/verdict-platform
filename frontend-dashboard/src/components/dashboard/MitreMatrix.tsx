import { useEffect, useMemo, useState } from "react";

import { getDetectionCoverage } from "../../services/dashboardService";
import type { CoverageItem } from "../../services/dashboardService";

type StatusFilter = "All" | "Detected" | "Partial" | "Missed";

export default function MitreMatrix() {
  const [coverage, setCoverage] = useState<CoverageItem[]>([]);
  const [statusFilter, setStatusFilter] =
    useState<StatusFilter>("All");
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedTechnique, setSelectedTechnique] =
    useState<string | null>(null);

  useEffect(() => {
    getDetectionCoverage()
      .then(setCoverage)
      .catch((error) => {
        console.error("Error loading MITRE coverage:", error);
      });
  }, []);

  /*
   * Build the tactic list dynamically from backend data.
   */
  const tactics = useMemo(() => {
    return Array.from(
      new Set(
        coverage
          .map((item) => item.tactic)
          .filter(Boolean)
      )
    ).sort();
  }, [coverage]);

  /*
   * Filter techniques by status and search.
   */
  const filteredCoverage = useMemo(() => {
    const search = searchTerm.trim().toLowerCase();

    return coverage.filter((item) => {
      const matchesStatus =
        statusFilter === "All" ||
        item.status === statusFilter;

      const matchesSearch =
        search === "" ||
        item.technique.toLowerCase().includes(search) ||
        item.name.toLowerCase().includes(search) ||
        item.rule_name.toLowerCase().includes(search) ||
        item.status.toLowerCase().includes(search) ||
        (search === "detected" && item.detected > 0) ||
        (search === "partial" && item.partial > 0) ||
        (search === "missed" && item.missed > 0);

      return matchesStatus && matchesSearch;
    });
  }, [coverage, statusFilter, searchTerm]);

  const selectedItem = coverage.find(
    (item) => item.technique === selectedTechnique
  );

  const getColor = (status: string) => {
    switch (status) {
      case "Detected":
        return "#d1fae5";

      case "Partial":
        return "#fef3c7";

      case "Missed":
        return "#fee2e2";

      default:
        return "#f3f4f6";
    }
  };

  const getBorderColor = (status: string) => {
    switch (status) {
      case "Detected":
        return "#10b981";

      case "Partial":
        return "#f59e0b";

      case "Missed":
        return "#ef4444";

      default:
        return "#d1d5db";
    }
  };

  return (
    <div style={{ marginTop: 40 }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 16,
          gap: 16,
          flexWrap: "wrap",
        }}
      >
        <div>
          <h2>MITRE ATT&CK Matrix</h2>

          <p
            style={{
              color: "#6b7280",
              fontSize: 14,
              marginTop: 4,
            }}
          >
            Detection coverage mapped to MITRE ATT&CK tactics
            and techniques.
          </p>
        </div>

        <select
          value={statusFilter}
          onChange={(event) =>
            setStatusFilter(
              event.target.value as StatusFilter
            )
          }
          style={{
            padding: "8px 12px",
            border: "1px solid #d1d5db",
            borderRadius: 6,
            background: "white",
          }}
        >
          <option value="All">All Statuses</option>
          <option value="Detected">Detected</option>
          <option value="Partial">Partial</option>
          <option value="Missed">Missed</option>
        </select>
      </div>

      {/* Search */}
      <div style={{ marginBottom: 20 }}>
        <input
          type="text"
          value={searchTerm}
          onChange={(event) =>
            setSearchTerm(event.target.value)
          }
          placeholder="Search technique, tactic or rule..."
          style={{
            width: "100%",
            maxWidth: 500,
            padding: "10px 12px",
            border: "1px solid #d1d5db",
            borderRadius: 6,
          }}
        />
      </div>

      {/* Legend */}
      <div
        style={{
          display: "flex",
          gap: 20,
          flexWrap: "wrap",
          marginBottom: 20,
          fontSize: 14,
        }}
      >
        <span>🟢 Detected</span>
        <span>🟡 Partial</span>
        <span>🔴 Missed</span>
      </div>

      {/* Matrix */}
      {filteredCoverage.length === 0 ? (
        <div
          style={{
            border: "1px solid #d1d5db",
            borderRadius: 8,
            padding: 24,
            textAlign: "center",
            color: "#6b7280",
          }}
        >
          No MITRE coverage data matches the selected filters.
        </div>
      ) : (
        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              "repeat(auto-fit, minmax(260px, 1fr))",
            gap: 20,
          }}
        >
          {tactics.map((tactic) => {
            const tacticItems = filteredCoverage.filter(
              (item) => item.tactic === tactic
            );

            if (tacticItems.length === 0) {
              return null;
            }

            return (
              <div key={tactic}>
                <h3
                  style={{
                    marginBottom: 12,
                    fontSize: 18,
                    fontWeight: 600,
                  }}
                >
                  {tactic}
                </h3>

                {tacticItems.map((item) => {
                  const isSelected =
                    selectedTechnique === item.technique;

                  return (
                    <button
                      key={`${item.technique}-${item.rule_name}`}
                      type="button"
                      onClick={() =>
                        setSelectedTechnique(
                          item.technique
                        )
                      }
                      style={{
                        width: "100%",
                        textAlign: "left",
                        background: getColor(item.status),
                        border: `2px solid ${getBorderColor(
                          item.status
                        )}`,
                        borderRadius: 8,
                        padding: 14,
                        marginBottom: 12,
                        cursor: "pointer",
                        boxShadow: isSelected
                          ? "0 0 0 2px #3b82f6"
                          : "none",
                      }}
                    >
                      <div
                        style={{
                          display: "flex",
                          justifyContent:
                            "space-between",
                          gap: 8,
                        }}
                      >
                        <strong>
                          {item.technique}
                        </strong>

                        <span
                          style={{
                            fontSize: 12,
                            fontWeight: 600,
                            background: "white",
                            padding: "3px 7px",
                            borderRadius: 999,
                          }}
                        >
                          {item.status}
                        </span>
                      </div>

                      <div
                        style={{
                          marginTop: 6,
                          fontSize: 14,
                        }}
                      >
                        {item.name}
                      </div>

                      <div
                        style={{
                          marginTop: 8,
                          fontSize: 12,
                          color: "#4b5563",
                        }}
                      >
                        Rule: {item.rule_name}
                      </div>
                    </button>
                  );
                })}
              </div>
            );
          })}
        </div>
      )}

      {/* Selected technique */}
      {selectedItem && (
        <div
          style={{
            marginTop: 24,
            border: "1px solid #d1d5db",
            borderRadius: 8,
            padding: 20,
            background: "white",
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "flex-start",
              gap: 16,
            }}
          >
            <div>
              <h3>Selected Technique</h3>

              <h4
                style={{
                  marginTop: 6,
                  fontSize: 20,
                }}
              >
                {selectedItem.technique}
              </h4>

              <p
                style={{
                  color: "#6b7280",
                  marginTop: 4,
                }}
              >
                {selectedItem.name}
              </p>
            </div>

            <button
              type="button"
              onClick={() =>
                setSelectedTechnique(null)
              }
              style={{
                padding: "6px 12px",
                border: "1px solid #d1d5db",
                borderRadius: 6,
                background: "white",
                cursor: "pointer",
              }}
            >
              Clear
            </button>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns:
                "repeat(auto-fit, minmax(160px, 1fr))",
              gap: 16,
              marginTop: 20,
            }}
          >
            <div>
              <small>MITRE Tactic</small>
              <div>{selectedItem.tactic}</div>
            </div>

            <div>
              <small>Rule</small>
              <div>{selectedItem.rule_name}</div>
            </div>

            <div>
              <small>Status</small>
              <div>{selectedItem.status}</div>
            </div>

            <div>
              <small>Detection Count</small>
              <div>{selectedItem.detected}</div>
            </div>

            <div>
              <small>Partial Count</small>
              <div>{selectedItem.partial}</div>
            </div>

            <div>
              <small>Missed Count</small>
              <div>{selectedItem.missed}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
import { useEffect, useState } from "react";

import { getDetectionCoverage } from "../../services/dashboardService";
import type { CoverageItem } from "../../services/dashboardService";

export default function MitreMatrix() {
  const [coverage, setCoverage] = useState<CoverageItem[]>([]);

  useEffect(() => {
    getDetectionCoverage()
      .then(setCoverage)
      .catch(console.error);
  }, []);

  const tactics = [
    "Execution",
    "Persistence",
    "Credential Access",
  ];

  const getColor = (status: string) => {
    switch (status) {
      case "Detected":
        return "#d1fae5"; // green
      case "Partial":
        return "#fef3c7"; // amber
      case "Missed":
        return "#fee2e2"; // red
      default:
        return "#f3f4f6"; // gray
    }
  };

  return (
    <div style={{ marginTop: 40 }}>
      <h2>MITRE ATT&CK Matrix</h2>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(3, 1fr)",
          gap: "20px",
        }}
      >
        {tactics.map((tactic) => (
          <div key={tactic}>
            <h3>{tactic}</h3>

            {coverage
              .filter((item) => item.tactic === tactic)
              .map((item) => (
                <div
                  key={item.technique}
                  style={{
                    background: getColor(item.status),
                    border: "1px solid #ccc",
                    borderRadius: 8,
                    padding: 12,
                    marginBottom: 12,
                  }}
                >
                  <strong>{item.technique}</strong>

                  <div>{item.name}</div>

                  <small>{item.rule_name}</small>

                  <div style={{ marginTop: 8 }}>
                    <b>{item.status}</b>
                  </div>
                </div>
              ))}
          </div>
        ))}
      </div>
    </div>
  );
}
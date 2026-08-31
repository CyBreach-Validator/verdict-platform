import { useEffect, useState } from "react";
import { getConnectors } from "../../services/connectorService";
import type { Connector } from "../../services/connectorService";

export default function ConnectorStatusCard() {
  const [connectors, setConnectors] = useState<Connector[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchConnectors = async () => {
      try {
        setError(null);

        const data = await getConnectors();

        setConnectors(data);
      } catch (err) {
        console.error("Failed to load connectors:", err);
        setError("Unable to load SIEM connector health.");
      } finally {
        setLoading(false);
      }
    };

    fetchConnectors();
  }, []);

  const getStatusStyle = (status: string) => {
    switch (status.toLowerCase()) {
      case "healthy":
        return {
          backgroundColor: "#dcfce7",
          color: "#15803d",
          borderColor: "#86efac",
        };

      case "disconnected":
        return {
          backgroundColor: "#fee2e2",
          color: "#dc2626",
          borderColor: "#fca5a5",
        };

      case "connecting":
        return {
          backgroundColor: "#fef3c7",
          color: "#d97706",
          borderColor: "#fcd34d",
        };

      default:
        return {
          backgroundColor: "#f3f4f6",
          color: "#374151",
          borderColor: "#d1d5db",
        };
    }
  };

  const getStatusIndicator = (status: string) => {
    switch (status.toLowerCase()) {
      case "healthy":
        return "●";

      case "disconnected":
        return "●";

      case "connecting":
        return "●";

      default:
        return "●";
    }
  };

  const healthyCount = connectors.filter(
    (connector) =>
      connector.status.toLowerCase() === "healthy"
  ).length;

  const disconnectedCount = connectors.filter(
    (connector) =>
      connector.status.toLowerCase() === "disconnected"
  ).length;

  const connectingCount = connectors.filter(
    (connector) =>
      connector.status.toLowerCase() === "connecting"
  ).length;

  if (loading) {
    return (
      <div
        style={{
          border: "1px solid #ddd",
          borderRadius: "10px",
          padding: "24px",
          marginBottom: "30px",
          backgroundColor: "#fff",
        }}
      >
        <h2 style={{ marginTop: 0 }}>
          SIEM Connector Health
        </h2>

        <p style={{ color: "#666", marginBottom: 0 }}>
          Loading connector health...
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div
        style={{
          border: "1px solid #fca5a5",
          borderRadius: "10px",
          padding: "24px",
          marginBottom: "30px",
          backgroundColor: "#fff5f5",
        }}
      >
        <h2 style={{ marginTop: 0 }}>
          SIEM Connector Health
        </h2>

        <p
          style={{
            color: "#b91c1c",
            marginBottom: 0,
          }}
        >
          {error}
        </p>
      </div>
    );
  }

  return (
    <div
      style={{
        border: "1px solid #ddd",
        borderRadius: "10px",
        padding: "24px",
        marginBottom: "30px",
        backgroundColor: "#fff",
        boxSizing: "border-box",
        width: "100%",
      }}
    >
      {/* Header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          gap: "20px",
          marginBottom: "24px",
          flexWrap: "wrap",
        }}
      >
        <div>
          <h2 style={{ margin: "0 0 6px" }}>
            SIEM Connector Health
          </h2>

          <p
            style={{
              margin: 0,
              color: "#666",
              fontSize: "14px",
            }}
          >
            Monitor the connection status of registered SIEM
            integrations.
          </p>
        </div>

        <div
          style={{
            padding: "8px 14px",
            borderRadius: "999px",
            backgroundColor: "#f3f4f6",
            color: "#374151",
            fontSize: "13px",
            fontWeight: "bold",
          }}
        >
          {connectors.length} Connector
          {connectors.length !== 1 ? "s" : ""}
        </div>
      </div>

      {/* Health Summary */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns:
            "repeat(auto-fit, minmax(150px, 1fr))",
          gap: "12px",
          marginBottom: "24px",
        }}
      >
        <div
          style={{
            border: "1px solid #86efac",
            borderRadius: "8px",
            padding: "16px",
            backgroundColor: "#f0fdf4",
          }}
        >
          <div
            style={{
              fontSize: "12px",
              color: "#166534",
              textTransform: "uppercase",
              fontWeight: "bold",
            }}
          >
            Healthy
          </div>

          <div
            style={{
              fontSize: "26px",
              fontWeight: "bold",
              marginTop: "6px",
              color: "#15803d",
            }}
          >
            {healthyCount}
          </div>
        </div>

        <div
          style={{
            border: "1px solid #fcd34d",
            borderRadius: "8px",
            padding: "16px",
            backgroundColor: "#fffbeb",
          }}
        >
          <div
            style={{
              fontSize: "12px",
              color: "#92400e",
              textTransform: "uppercase",
              fontWeight: "bold",
            }}
          >
            Connecting
          </div>

          <div
            style={{
              fontSize: "26px",
              fontWeight: "bold",
              marginTop: "6px",
              color: "#d97706",
            }}
          >
            {connectingCount}
          </div>
        </div>

        <div
          style={{
            border: "1px solid #fca5a5",
            borderRadius: "8px",
            padding: "16px",
            backgroundColor: "#fef2f2",
          }}
        >
          <div
            style={{
              fontSize: "12px",
              color: "#991b1b",
              textTransform: "uppercase",
              fontWeight: "bold",
            }}
          >
            Disconnected
          </div>

          <div
            style={{
              fontSize: "26px",
              fontWeight: "bold",
              marginTop: "6px",
              color: "#dc2626",
            }}
          >
            {disconnectedCount}
          </div>
        </div>
      </div>

      {/* Connector List */}
      {connectors.length === 0 ? (
        <div
          style={{
            padding: "30px",
            textAlign: "center",
            border: "1px dashed #ccc",
            borderRadius: "8px",
            color: "#666",
          }}
        >
          No SIEM connectors registered.
        </div>
      ) : (
        <div
          style={{
            display: "grid",
            gap: "12px",
          }}
        >
          {connectors.map((connector) => {
            const statusStyle = getStatusStyle(
              connector.status
            );

            return (
              <div
                key={connector.id}
                style={{
                  border: "1px solid #e5e7eb",
                  borderRadius: "8px",
                  padding: "18px",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  gap: "20px",
                  flexWrap: "wrap",
                }}
              >
                {/* Connector Information */}
                <div
                  style={{
                    minWidth: 0,
                    flex: "1 1 250px",
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "10px",
                    }}
                  >
                    <h3
                      style={{
                        margin: 0,
                        fontSize: "17px",
                      }}
                    >
                      {connector.name}
                    </h3>

                    <span
                      style={{
                        fontSize: "12px",
                        color: "#777",
                        backgroundColor: "#f3f4f6",
                        padding: "3px 8px",
                        borderRadius: "999px",
                      }}
                    >
                      ID {connector.id}
                    </span>
                  </div>

                  <div
                    style={{
                      display: "flex",
                      gap: "20px",
                      flexWrap: "wrap",
                      marginTop: "8px",
                      fontSize: "13px",
                      color: "#666",
                    }}
                  >
                    <span>
                      <strong>Version:</strong>{" "}
                      {connector.version || "N/A"}
                    </span>

                    <span>
                      <strong>Last Seen:</strong>{" "}
                      {connector.last_seen
                        ? new Date(
                            connector.last_seen
                          ).toLocaleString()
                        : "N/A"}
                    </span>
                  </div>
                </div>

                {/* Status */}
                <div
                  style={{
                    ...statusStyle,
                    border: "1px solid",
                    padding: "8px 16px",
                    borderRadius: "999px",
                    fontWeight: "bold",
                    fontSize: "13px",
                    minWidth: "125px",
                    textAlign: "center",
                    boxSizing: "border-box",
                  }}
                >
                  {getStatusIndicator(
                    connector.status
                  )}{" "}
                  {connector.status}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

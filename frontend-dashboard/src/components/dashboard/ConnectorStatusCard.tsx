import { useEffect, useState } from "react";
import { getConnectors } from "../../services/connectorService";
import type { Connector } from "../../services/connectorService";

export default function ConnectorStatusCard() {
  const [connectors, setConnectors] = useState<Connector[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchConnectors = async () => {
      try {
        const data = await getConnectors();
        setConnectors(data);
      } catch (error) {
        console.error("Failed to load connectors:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchConnectors();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Healthy":
        return {
          backgroundColor: "#dcfce7",
          color: "#15803d",
        };

      case "Disconnected":
        return {
          backgroundColor: "#fee2e2",
          color: "#dc2626",
        };

      case "Connecting":
        return {
          backgroundColor: "#fef3c7",
          color: "#d97706",
        };

      default:
        return {
          backgroundColor: "#f3f4f6",
          color: "#374151",
        };
    }
  };

  if (loading) {
    return (
      <div
        style={{
          border: "1px solid #ddd",
          borderRadius: "8px",
          padding: "20px",
          marginBottom: "30px",
        }}
      >
        Loading SIEM connectors...
      </div>
    );
  }

  return (
    <div
      style={{
        border: "1px solid #ddd",
        borderRadius: "8px",
        padding: "20px",
        marginBottom: "30px",
        backgroundColor: "#fff",
      }}
    >
      <h2 style={{ marginBottom: "20px" }}>SIEM Connector Status</h2>

      {connectors.map((connector) => (
        <div
          key={connector.id}
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            padding: "15px 0",
            borderBottom: "1px solid #e5e5e5",
          }}
        >
          <div>
            <h3 style={{ margin: 0 }}>{connector.name}</h3>

            <p
              style={{
                margin: "6px 0",
                color: "#666",
              }}
            >
              Version {connector.version}
            </p>

            <p
              style={{
                margin: 0,
                color: "#888",
                fontSize: "14px",
              }}
            >
              Last Seen:{" "}
              {connector.last_seen
                ? new Date(connector.last_seen).toLocaleString()
                : "N/A"}
            </p>
          </div>

          <span
            style={{
              ...getStatusColor(connector.status),
              padding: "8px 18px",
              borderRadius: "999px",
              fontWeight: "bold",
              minWidth: "130px",
              textAlign: "center",
            }}
          >
            {connector.status}
          </span>
        </div>
      ))}
    </div>
  );
}
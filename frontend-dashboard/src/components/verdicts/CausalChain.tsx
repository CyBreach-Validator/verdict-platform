import { useEffect, useState } from "react";

import {
  getCausalChain,
  type CausalChain,
} from "../../services/causalChainService";

interface Props {
  verdictId: number;
}

export default function CausalChain({ verdictId }: Props) {
  const [chain, setChain] = useState<CausalChain | null>(null);

  useEffect(() => {
    getCausalChain(verdictId)
      .then(setChain)
      .catch(console.error);
  }, [verdictId]);

  if (!chain) {
    return <p>Loading causal chain...</p>;
  }

  return (
    <div style={{ marginTop: 40 }}>
      <h2>Causal Chain</h2>

      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: 20,
        }}
      >
        <Node
          title="Sigma Rule"
          value={`${chain.rule.name} (${chain.rule.technique})`}
        />

        <Arrow />

        <Node
          title="Evidence Event"
          value={JSON.stringify(chain.event)}
        />

        <Arrow />

        <Node
          title="Validation Engine"
          value={chain.validation.status}
        />

        <Arrow />

        <Node
          title="Outcome Classifier"
          value={chain.classifier.status}
        />

        <Arrow />

        <Node
          title="Verdict"
          value={`ID ${chain.verdict.id}`}
        />
      </div>
    </div>
  );
}

function Arrow() {
  return (
    <div
      style={{
        fontSize: 28,
        textAlign: "center",
      }}
    >
      ↓
    </div>
  );
}

function Node({
  title,
  value,
}: {
  title: string;
  value: string;
}) {
  return (
    <div
      style={{
        border: "1px solid #ddd",
        borderRadius: 10,
        padding: 20,
        background: "#fafafa",
      }}
    >
      <strong>{title}</strong>

      <div
        style={{
          marginTop: 10,
        }}
      >
        {value}
      </div>
    </div>
  );
}
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
    if (!id) return;

    setLoading(true);

    getVerdict(Number(id))
      .then((data) => {
        setVerdict(data);
      })
      .catch((err) => {
        console.error("Failed to load verdict:", err);
        setVerdict(null);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [id]);

  const handleRevalidate = async () => {
    if (!verdict || revalidating) return;

    setRevalidating(true);
    setRevalidationError(null);
    setRevalidationResult(null);

    try {
      const result = await revalidateVerdict(verdict.id);

      setRevalidationResult(result);

      // Refresh original verdict so supersession
      // information is immediately reflected.
      const updatedVerdict = await getVerdict(verdict.id);

      setVerdict(updatedVerdict);
    } catch (err) {
      console.error("Re-validation failed:", err);

      setRevalidationError(
        "Re-validation failed. Please try again."
      );
    } finally {
      setRevalidating(false);
    }
  };

  const getVerdictClass = (value: string) => {
    switch (value.toLowerCase()) {
      case "detected":
        return "verdict-badge verdict-detected";

      case "missed":
        return "verdict-badge verdict-missed";

      case "partial":
        return "verdict-badge verdict-partial";

      case "no data":
        return "verdict-badge verdict-no-data";

      default:
        return "verdict-badge";
    }
  };

  const formatEventData = () => {
    try {
      return JSON.stringify(
        JSON.parse(verdict?.event_data || "{}"),
        null,
        2
      );
    } catch {
      return verdict?.event_data || "No event data available.";
    }
  };

  if (loading) {
    return (
      <div className="verdict-page">
        <div className="verdict-loading">
          Loading verdict details...
        </div>
      </div>
    );
  }

  if (!verdict) {
    return (
      <div className="verdict-page">
        <div className="verdict-error">
          <h2>Verdict not found</h2>

          <Link to="/dashboard">
            ← Back to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="verdict-page">
      {/* Header */}
      <div className="verdict-header">
        <div>
          <Link
            to="/dashboard"
            className="back-link"
          >
            ← Back to Dashboard
          </Link>

          <h1>Verdict Details</h1>

          <p className="verdict-subtitle">
            Detailed validation result for verdict #{verdict.id}
          </p>
        </div>

        <div className={getVerdictClass(verdict.verdict)}>
          {verdict.verdict}
        </div>
      </div>

      {/* Overview */}
      <section className="verdict-section">
        <div className="section-header">
          <h2>Overview</h2>
        </div>

        <div className="details-grid">
          <div className="detail-card">
            <span className="detail-label">
              Verdict ID
            </span>
            <strong>{verdict.id}</strong>
          </div>

          <div className="detail-card">
            <span className="detail-label">
              Rule ID
            </span>
            <strong>{verdict.rule_id}</strong>
          </div>

          <div className="detail-card">
            <span className="detail-label">
              Rule Name
            </span>
            <strong>{verdict.rule_name}</strong>
          </div>

          <div className="detail-card">
            <span className="detail-label">
              Verdict
            </span>
            <span className={getVerdictClass(verdict.verdict)}>
              {verdict.verdict}
            </span>
          </div>

          <div className="detail-card">
            <span className="detail-label">
              Created At
            </span>
            <strong>
              {new Date(
                verdict.created_at
              ).toLocaleString()}
            </strong>
          </div>

          <div className="detail-card">
            <span className="detail-label">
              Superseded
            </span>

            <strong>
              {verdict.is_superseded ? "Yes" : "No"}
            </strong>
          </div>

          <div className="detail-card">
            <span className="detail-label">
              Superseded By
            </span>

            <strong>
              {verdict.superseded_by ?? "—"}
            </strong>
          </div>

          <div className="detail-card detail-card-wide">
            <span className="detail-label">
              Verdict Hash
            </span>

            <code className="hash-value">
              {verdict.verdict_hash}
            </code>
          </div>
        </div>
      </section>

      {/* Re-validation */}
      <section className="verdict-section">
        <div className="section-header">
          <div>
            <h2>Re-Validation</h2>

            <p>
              Re-run validation against the current rule
              and compare the result with this verdict.
            </p>
          </div>

          <button
            onClick={handleRevalidate}
            disabled={revalidating}
            className="revalidate-button"
          >
            {revalidating
              ? "Re-validating..."
              : "Re-Validate"}
          </button>
        </div>

        {revalidationError && (
          <div className="revalidation-error">
            {revalidationError}
          </div>
        )}

        {revalidationResult && (
          <div className="comparison-container">
            <h3>Before / After Comparison</h3>

            <div className="comparison-grid">
              <div className="comparison-card">
                <span>Original Verdict</span>

                <strong
                  className={getVerdictClass(
                    revalidationResult.old_verdict.verdict
                  )}
                >
                  {revalidationResult.old_verdict.verdict}
                </strong>

                <small>
                  Score:{" "}
                  {revalidationResult.comparison.old_score}
                </small>
              </div>

              <div className="comparison-arrow">
                →
              </div>

              <div className="comparison-card">
                <span>New Verdict</span>

                <strong
                  className={getVerdictClass(
                    revalidationResult.new_verdict.verdict
                  )}
                >
                  {revalidationResult.new_verdict.verdict}
                </strong>

                <small>
                  Score:{" "}
                  {revalidationResult.comparison.new_score}
                </small>
              </div>
            </div>

            <div className="comparison-summary">
              <div>
                  <span>Score Delta</span>
                  <strong>
                    {revalidationResult.comparison.delta > 0 ? "+" : ""}
                    {revalidationResult.comparison.delta}
                 </strong>
                </div>

              <div>
                <span>Improved</span>
                <strong>
                  {revalidationResult.comparison.improved
                    ? "Yes"
                    : "No"}
                </strong>
              </div>

              <div>
                <span>Gap Closed</span>
                <strong>
                  {revalidationResult.comparison.gap_closed
                    ? "Yes"
                    : "No"}
                </strong>
              </div>

              <div>
                <span>New Verdict ID</span>
                <strong>
                  {revalidationResult.new_verdict.id}
                </strong>
              </div>
            </div>

            <div className="revalidation-metadata">
              <div>
                <span>Validation Status</span>
                <strong>
                  {revalidationResult.validation.status}
                </strong>
              </div>

              <div>
                <span>New Verdict Hash</span>
                <code>
                  {revalidationResult.new_verdict.verdict_hash}
                </code>
                
              </div>
            </div>
          </div>
        )}
      </section>

      {/* Event Data */}
      <section className="verdict-section">
        <div className="section-header">
          <div>
            <h2>Event Data</h2>

            <p>
              Raw evidence event associated with this verdict.
            </p>
          </div>
        </div>

        <pre className="event-data">
          {formatEventData()}
        </pre>
      </section>

      {/* Timeline */}
      <section className="verdict-section">
        <div className="section-header">
          <div>
            <h2>Verdict Timeline</h2>

            <p>
              Chronological history of this verdict and
              related re-validation activity.
            </p>
          </div>
        </div>

        <VerdictTimeline
          verdict={verdict}
          revalidationResult={revalidationResult}
        />
      </section>

      {/* Causal Chain */}
      <section className="verdict-section">
        <div className="section-header">
          <div>
            <h2>Causal Chain</h2>

            <p>
              Validation path connecting the evidence,
              rule evaluation, and resulting verdict.
            </p>
          </div>
        </div>

        <CausalChain verdictId={verdict.id} />
      </section>

    </div>
  );
}

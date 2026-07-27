import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import VerdictTable from "../components/VerdictTable";
import VerdictFilter from "../components/VerdictFilter";
import Pagination from "../components/Pagination";
import CoverageHeatmap from "../components/dashboard/CoverageHeatmap";
import MitreMatrix from "../components/dashboard/MitreMatrix";

interface Verdict {
  id: number;
  rule_name: string;
  verdict: string;
  created_at: string;
}

function Dashboard() {
  const [verdicts, setVerdicts] = useState<Verdict[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedStatus, setSelectedStatus] = useState("All");

  // Pagination State
  const [currentPage, setCurrentPage] = useState(1);
  const verdictsPerPage = 10;

  const navigate = useNavigate();

  useEffect(() => {
    api
      .get("/verdicts")
      .then((response) => {
        setVerdicts(response.data);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error fetching verdicts:", error);
        setLoading(false);
      });
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    navigate("/");
  };

  const detectedCount = verdicts.filter(
    (v) => v.verdict === "Detected"
  ).length;

  const missedCount = verdicts.filter(
    (v) => v.verdict === "Missed"
  ).length;

  const partialCount = verdicts.filter(
    (v) => v.verdict === "Partial"
  ).length;

  // Apply Filter
  const filteredVerdicts =
    selectedStatus === "All"
      ? verdicts
      : verdicts.filter((v) => v.verdict === selectedStatus);

  // Pagination
  const totalPages = Math.ceil(filteredVerdicts.length / verdictsPerPage);

  const indexOfLastVerdict = currentPage * verdictsPerPage;
  const indexOfFirstVerdict = indexOfLastVerdict - verdictsPerPage;

  const currentVerdicts = filteredVerdicts.slice(
    indexOfFirstVerdict,
    indexOfLastVerdict
  );

  return (
    <div style={{ padding: "30px" }}>
      <h1>CyBreach Validator Dashboard</h1>

      <button
        onClick={handleLogout}
        style={{
          marginBottom: "20px",
          padding: "8px 16px",
          cursor: "pointer",
        }}
      >
        Logout
      </button>

      {/* Summary Cards */}
      <div
        style={{
          display: "flex",
          gap: "20px",
          marginBottom: "30px",
          flexWrap: "wrap",
        }}
      >
        <div
          style={{
            border: "1px solid #ccc",
            borderRadius: "8px",
            padding: "20px",
            width: "180px",
            backgroundColor: "#f8f9fa",
          }}
        >
          <h3>Total Verdicts</h3>
          <h1>{verdicts.length}</h1>
        </div>

        <div
          style={{
            border: "1px solid green",
            borderRadius: "8px",
            padding: "20px",
            width: "180px",
            backgroundColor: "#f0fff4",
          }}
        >
          <h3>Detected</h3>
          <h1 style={{ color: "green" }}>{detectedCount}</h1>
        </div>

        <div
          style={{
            border: "1px solid red",
            borderRadius: "8px",
            padding: "20px",
            width: "180px",
            backgroundColor: "#fff5f5",
          }}
        >
          <h3>Missed</h3>
          <h1 style={{ color: "red" }}>{missedCount}</h1>
        </div>

        <div
          style={{
            border: "1px solid orange",
            borderRadius: "8px",
            padding: "20px",
            width: "180px",
            backgroundColor: "#fffaf0",
          }}
        >
          <h3>Partial</h3>
          <h1 style={{ color: "orange" }}>{partialCount}</h1>
        </div>
      </div>

      <h2>Verdicts</h2>

      <VerdictFilter
        selectedStatus={selectedStatus}
        onStatusChange={(status) => {
          setSelectedStatus(status);
          setCurrentPage(1); // Reset to first page when filter changes
        }}
      />

      {loading ? (
        <p>Loading...</p>
      ) : (
        <>
          <VerdictTable verdicts={currentVerdicts} />

          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={setCurrentPage}
          />
          <MitreMatrix />
        </>
      )}
    </div>
  );
}

export default Dashboard;
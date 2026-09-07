import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import VerdictTable from "../components/VerdictTable";
import VerdictFilter from "../components/VerdictFilter";
import Pagination from "../components/Pagination";
import CoverageHeatmap from "../components/dashboard/CoverageHeatmap";
import MitreMatrix from "../components/dashboard/MitreMatrix";
import ConnectorStatusCard from "../components/dashboard/ConnectorStatusCard";
import websocketService from "../services/websocketService";
import { exportCSV, exportPDF } from "../services/exportService";

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

  useEffect(() => {

  websocketService.connect(

    (data) => {

  console.log("📩 WebSocket Message:", data);

  setVerdicts((previousVerdicts) => {

    const alreadyExists = previousVerdicts.some(
      (v) => v.id === data.id
    );

    if (alreadyExists) {
      return previousVerdicts;
    }

    return [data, ...previousVerdicts];

  });

},

    () => {

      console.log("🟢 Connected");

    },

    () => {

      console.log("🔴 Disconnected");

    }

  );

  return () => {

    websocketService.disconnect();

  };

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
    <div className="dashboard-container">
      <h1 className="dashboard-title">CyBreach Validator Dashboard</h1>

      <button
        onClick={handleLogout}
        className="dashboard-logout"
      >
        Logout
      </button>

      {/* Summary Cards */}
      <div className="summary-cards">
      
        <div className="summary-card">
         <h3>Total Verdicts</h3>
         <h1>{verdicts.length}</h1>
        </div>

        <div className="summary-card detected-card">
          <h3>Detected</h3>
          <h1 style={{ color: "green" }}>{detectedCount}</h1>
        </div>

        <div className="summary-card missed-card">
          <h3>Missed</h3>
          <h1 style={{ color: "red" }}>{missedCount}</h1>
        </div>

       <div className="summary-card partial-card">
          <h3>Partial</h3>
          <h1 style={{ color: "orange" }}>{partialCount}</h1>
        </div>
      </div>
      <ConnectorStatusCard />
      <h2 className="section-title">Verdicts</h2>

      <VerdictFilter
        selectedStatus={selectedStatus}
        onStatusChange={(status) => {
          setSelectedStatus(status);
          setCurrentPage(1); // Reset to first page when filter changes
        }}
      />

     <div className="export-buttons">

  <button
    onClick={exportCSV}
    className="export-button"
  >
    Export CSV
  </button>

    <button
    onClick={exportPDF}
    className="export-button"
  >
    Export PDF
  </button>
</div>

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

          <CoverageHeatmap />

          <MitreMatrix />
        </>
      )}
    </div>
  );
}

export default Dashboard;
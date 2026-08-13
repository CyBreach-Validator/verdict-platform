import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Login from "../pages/Login";
import Dashboard from "../pages/Dashboard";
import VerdictDetails from "../pages/VerdictDetails";
import RuleManagement from "../pages/RuleManagement";
import RevalidationDashboard from "../pages/RevalidationDashboard";

function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/verdicts/:id" element={<VerdictDetails />} />
        <Route path="/rules" element={<RuleManagement />} />
        <Route
          path="/revalidation"
          element={<RevalidationDashboard />}
        />

        <Route
          path="*"
          element={<Navigate to="/" />}
        />
      </Routes>
    </BrowserRouter>
  );
}

export default AppRoutes;
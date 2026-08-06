import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Login from "../pages/Login";
import Dashboard from "../pages/Dashboard";
import VerdictDetails from "../pages/VerdictDetails";
import RuleManagement from "../pages/RuleManagement";

function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/verdicts/:id" element={<VerdictDetails />} />
        <Route path="/rules" element={<RuleManagement />} />

        {/* Keep this LAST */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default AppRoutes;
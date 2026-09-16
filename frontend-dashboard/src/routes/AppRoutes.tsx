import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Login from "../pages/Login";
import Dashboard from "../pages/Dashboard";
import VerdictDetails from "../pages/VerdictDetails";
import RuleManagement from "../pages/RuleManagement";
import RevalidationDashboard from "../pages/RevalidationDashboard";
import MainLayout from "../layouts/MainLayout";

function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />

        <Route
          path="/dashboard"
          element={
            <MainLayout>
              <Dashboard />
            </MainLayout>
          }
        />

        <Route
          path="/verdicts/:id"
          element={
            <MainLayout>
              <VerdictDetails />
            </MainLayout>
          }
        />

        <Route
          path="/rules"
          element={
            <MainLayout>
              <RuleManagement />
            </MainLayout>
          }
        />

        <Route
          path="/revalidation"
          element={
            <MainLayout>
              <RevalidationDashboard />
            </MainLayout>
          }
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
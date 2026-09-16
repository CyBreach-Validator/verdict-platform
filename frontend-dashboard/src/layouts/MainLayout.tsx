import type { ReactNode } from "react";
import Sidebar from "./Sidebar";

interface MainLayoutProps {
  children: ReactNode;
}

function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className="flex min-h-screen flex-col bg-gray-50 md:flex-row">
      <Sidebar />

      <main className="min-w-0 flex-1 overflow-x-auto">
        {children}
      </main>
    </div>
  );
}

export default MainLayout;
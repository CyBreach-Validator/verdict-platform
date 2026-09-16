import { NavLink } from "react-router-dom";

function Sidebar() {
  return (
    <aside
      className="w-full shrink-0 border-b border-gray-200 bg-white md:w-64 md:border-b-0 md:border-r"
      aria-label="Main navigation"
    >
      <div className="border-b border-gray-200 p-4">
        <h2 className="text-lg font-bold text-gray-900">
          CyBreach Validator
        </h2>
      </div>

      <nav className="p-3">
        <ul className="flex flex-wrap gap-2 md:block md:space-y-2">
          <li>
            <NavLink
              to="/dashboard"
              className={({ isActive }) =>
                `block rounded-md px-4 py-3 text-sm font-medium transition
                focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2
                ${
                  isActive
                    ? "bg-blue-100 text-blue-900"
                    : "text-gray-700 hover:bg-gray-100"
                }`
              }
            >
              Dashboard
            </NavLink>
          </li>

          <li>
            <NavLink
              to="/rules"
              className={({ isActive }) =>
                `block rounded-md px-4 py-3 text-sm font-medium transition
                focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2
                ${
                  isActive
                    ? "bg-blue-100 text-blue-900"
                    : "text-gray-700 hover:bg-gray-100"
                }`
              }
            >
              Rule Management
            </NavLink>
          </li>

          <li>
            <NavLink
              to="/revalidation"
              className={({ isActive }) =>
                `block rounded-md px-4 py-3 text-sm font-medium transition
                focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2
                ${
                  isActive
                    ? "bg-blue-100 text-blue-900"
                    : "text-gray-700 hover:bg-gray-100"
                }`
              }
            >
              Revalidation
            </NavLink>
          </li>
        </ul>
      </nav>
    </aside>
  );
}

export default Sidebar;
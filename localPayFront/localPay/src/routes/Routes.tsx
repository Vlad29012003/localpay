import { createBrowserRouter } from "react-router-dom";
import App from "../App";
import HomePage from "../pages/HomePage";
import LoginPage from "../pages/LoginPage";
import AdminPanel from "../pages/admin/AdminPanel";
import UserRoleWarningPage from "../pages/user/UserRoleWarningPage";

import UserPanel from "../pages/user/UserPanel";
import UserProfile from "../pages/user/UserProfile";
import MakePayment from "../pages/user/MakePayment";
import SupervisorPanel from "../pages/SupervisorPanel";
import RegisterUserPage from "../pages/admin/RegisterUserPage";
import PaymentsPage from "../pages/admin/PaymentsPage";
import ReportsPage from "../pages/admin/ReportsPage";
import UsersPage from "../pages/admin/UsersPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: (
        <App />
    ),
    children: [
      { path: "", element: <HomePage /> },
      { path: "/login", element: <LoginPage /> },
      { path: "/restricted", element: <UserRoleWarningPage /> },
      { path: "/admin", element: <AdminPanel /> },
      { path: "/users", element: <UsersPage /> },
      { path: "/reports", element: <ReportsPage /> },
      { path: "/payments", element: <PaymentsPage /> },
      { path: "/user", element: <UserPanel /> },
      { path: "/profile", element: <UserProfile /> },
      { path: "/register", element: <RegisterUserPage /> },
      { path: "/makepayment", element: <MakePayment /> },
      { path: "/supervisor", element: <SupervisorPanel /> },
    ],
  },
]);

// src/hooks/useRoleRedirect.ts
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { jwtDecode } from "jwt-decode";
import { DecodedToken } from "../components/DecodedToken";

const useRoleRedirect = (requiredRoles: string[]) => {
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      navigate("/login");
      return;
    }

    try {
      const decodedToken: DecodedToken = jwtDecode(token || '');
      const userRole = decodedToken.role;

      if (!requiredRoles.includes(userRole)) {
        // Redirect to the appropriate page based on the user's role
        if (userRole === "admin") {
          navigate("/admin");
        } else if (userRole === "supervisor") {
          navigate("/supervisor");
        } else if (userRole === "user") {
          navigate("/user");
        } else {
          navigate("/login");
        }
      }
    } catch (error) {
      navigate("/login");
    }
  }, [navigate, requiredRoles]);
};

export default useRoleRedirect;

// handleLogout function
export const handleLogout = () => {
  localStorage.removeItem('token');
  window.location.href = '/login';
};

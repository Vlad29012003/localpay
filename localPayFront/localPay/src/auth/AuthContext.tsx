import React, { createContext, useContext, useEffect, useState } from 'react';
import { jwtDecode } from 'jwt-decode';
import { useNavigate, useLocation } from 'react-router-dom';

interface AuthContextType {
  isAdmin: boolean;
  token: string | null;
  logout: () => void;
  setAuthToken: (token: string | null) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAdmin, setIsAdmin] = useState<boolean>(false);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      setAuthToken(storedToken);
    } else {
      setLoading(false);
    }
  }, []);

  const setAuthToken = (newToken: string | null) => {
    if (newToken) {
      const decodedToken: any = jwtDecode(newToken);
      setIsAdmin(decodedToken.is_admin);
      setToken(newToken);
      localStorage.setItem('token', newToken);
      
      // Перенаправление после успешной аутентификации
      const from = location.state?.from?.pathname || (decodedToken.is_admin ? '/admin' : '/user');
      navigate(from, { replace: true });
    } else {
      setIsAdmin(false);
      setToken(null);
      localStorage.removeItem('token');
    }
    setLoading(false);
  };

  const logout = () => {
    setAuthToken(null);
    navigate('/', { replace: true });
  };

  if (loading) {
    return <div>Loading...</div>; // или ваш компонент загрузки
  }

  const contextValue: AuthContextType = {
    isAdmin,
    token,
    logout,
    setAuthToken
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
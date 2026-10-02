import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Format backend user model for application context
  const formatUser = (userData) => {
    if (!userData) return null;
    return {
      id: userData.id,
      name: userData.name,
      email: userData.email,
      role: userData.role || 'consumer',
      created_at: userData.created_at,
    };
  };

  // Verify stored token on app boot / browser refresh
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          const res = await authAPI.getCurrentUser();
          setUser(formatUser(res.data));
          setIsAuthenticated(true);
        } catch (err) {
          console.error("Session restoration failed:", err);
          localStorage.removeItem('token');
          setUser(null);
          setIsAuthenticated(false);
        }
      } else {
        setUser(null);
        setIsAuthenticated(false);
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email, password) => {
    setError(null);
    try {
      const response = await authAPI.login({ email, password });
      const { access_token, user: apiUser } = response.data;

      localStorage.setItem('token', access_token);
      const formattedUser = formatUser(apiUser);
      setUser(formattedUser);
      setIsAuthenticated(true);
      return formattedUser;
    } catch (err) {
      const errorMsg = err.response?.data?.detail || "Login failed. Please check your credentials.";
      setError(errorMsg);
      throw new Error(errorMsg);
    }
  };

  const register = async (name, email, password, role) => {
    setError(null);
    try {
      const response = await authAPI.register({ name, email, password, role });
      return response.data;
    } catch (err) {
      const errorMsg = err.response?.data?.detail || "Registration failed. Please check your inputs.";
      setError(errorMsg);
      throw new Error(errorMsg);
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setIsAuthenticated(false);
    setError(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        loading,
        error,
        login,
        register,
        logout,
        setError,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);

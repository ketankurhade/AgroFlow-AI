import React, { createContext, useContext, useState, useEffect } from 'react';
import { INITIAL_USER } from '../data/mockData';
import { authAPI } from '../services/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Format backend user model with mock metadata defaults (avatar, availableRoles, organization)
  const formatUser = (userData) => {
    if (!userData) return null;
    return {
      ...INITIAL_USER,
      ...userData,
      // Map backend role to user display role if needed
      role: userData.role || INITIAL_USER.role,
      organization: userData.organization || INITIAL_USER.organization,
      avatar: userData.avatar || INITIAL_USER.avatar,
      availableRoles: INITIAL_USER.availableRoles
    };
  };

  // Verify stored token on app boot
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

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setIsAuthenticated(false);
    setError(null);
  };

  const switchRole = (newRole) => {
    setUser((prev) => (prev ? { ...prev, role: newRole } : null));
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        loading,
        error,
        login,
        logout,
        switchRole,
        setError
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);

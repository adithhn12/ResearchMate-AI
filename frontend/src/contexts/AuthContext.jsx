import React, { createContext, useContext, useState, useEffect } from 'react';
import { authApi } from '../api/client';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    try {
      const saved = localStorage.getItem('researchmate_user');
      return saved && saved !== 'undefined' ? JSON.parse(saved) : null;
    } catch {
      localStorage.removeItem('researchmate_user');
      return null;
    }
  });
  const [token, setToken] = useState(() => localStorage.getItem('researchmate_token') || null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('researchmate_token');
      if (storedToken) {
        try {
          const res = await authApi.getMe();
          setUser(res.data);
          localStorage.setItem('researchmate_user', JSON.stringify(res.data));
        } catch (err) {
          console.error("Auth check failed:", err);
          logout();
        }
      }
      setLoading(false);
    };
    initAuth();
  }, []);

  const login = async (email, password) => {
    const res = await authApi.login(email, password);
    const { access_token, user: userData } = res.data;
    localStorage.setItem('researchmate_token', access_token);
    localStorage.setItem('researchmate_user', JSON.stringify(userData));
    setToken(access_token);
    setUser(userData);
    return userData;
  };

  const register = async (email, password, fullName) => {
    const res = await authApi.register(email, password, fullName);
    const { access_token, user: userData } = res.data;
    localStorage.setItem('researchmate_token', access_token);
    localStorage.setItem('researchmate_user', JSON.stringify(userData));
    setToken(access_token);
    setUser(userData);
    return userData;
  };

  const demoLogin = async () => {
    const res = await authApi.demoLogin();
    const { access_token, user: userData } = res.data;
    localStorage.setItem('researchmate_token', access_token);
    localStorage.setItem('researchmate_user', JSON.stringify(userData));
    setToken(access_token);
    setUser(userData);
    return userData;
  };

  const logout = () => {
    localStorage.removeItem('researchmate_token');
    localStorage.removeItem('researchmate_user');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{
      user,
      token,
      loading,
      isAuthenticated: !!token,
      login,
      register,
      demoLogin,
      logout
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authService } from '../services/authService';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('farmer_data');
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState(() => localStorage.getItem('access_token'));
  const [loading, setLoading] = useState(true);

  const fetchProfile = useCallback(async () => {
    try {
      const profile = await authService.getMe();
      setUser(profile);
      localStorage.setItem('farmer_data', JSON.stringify(profile));
    } catch {
      // Token invalid or expired
      localStorage.removeItem('access_token');
      localStorage.removeItem('farmer_data');
      setUser(null);
      setToken(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (token) {
      fetchProfile();
    } else {
      setLoading(false);
    }

    const handleUnauthorized = () => {
      setUser(null);
      setToken(null);
      localStorage.removeItem('access_token');
      localStorage.removeItem('farmer_data');
    };

    window.addEventListener('auth:unauthorized', handleUnauthorized);
    return () => window.removeEventListener('auth:unauthorized', handleUnauthorized);
  }, [token, fetchProfile]);

  const login = async (phone, password) => {
    const data = await authService.login(phone, password);
    const accessToken = data.access_token;
    localStorage.setItem('access_token', accessToken);
    setToken(accessToken);

    // Fetch user profile
    const profile = await authService.getMe();
    setUser(profile);
    localStorage.setItem('farmer_data', JSON.stringify(profile));
    return profile;
  };

  const register = async (payload) => {
    return await authService.register(payload);
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('farmer_data');
    setUser(null);
    setToken(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        isAuthenticated: !!token && !!user,
        login,
        register,
        logout,
        refreshProfile: fetchProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

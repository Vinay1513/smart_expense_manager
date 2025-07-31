import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in on app start
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      // You could verify the token here by making an API call
      setLoading(false);
    } else {
      setLoading(false);
    }
  }, [token]);

  const login = async (username, password) => {
    try {
      const response = await api.post('/auth/login/', {
        username,
        password,
      });
      
      const { access, refresh } = response.data;
      
      localStorage.setItem('token', access);
      localStorage.setItem('refreshToken', refresh);
      
      api.defaults.headers.common['Authorization'] = `Bearer ${access}`;
      setToken(access);
      
      // Get user info
      // You might want to add an endpoint to get current user info
      setUser({ username });
      
      return { success: true };
    } catch (error) {
      let errorMessage = 'Login failed';
      
      if (error.response?.data) {
        if (typeof error.response.data === 'string') {
          errorMessage = error.response.data;
        } else if (error.response.data.detail) {
          errorMessage = error.response.data.detail;
        } else if (typeof error.response.data === 'object') {
          errorMessage = Object.values(error.response.data).join(', ');
        }
      }
      
      return {
        success: false,
        error: errorMessage,
      };
    }
  };

  const register = async (userData) => {
    try {
      await api.post('/auth/register/', userData);
      
      // Auto-login after registration
      const loginResult = await login(userData.username, userData.password);
      return loginResult;
    } catch (error) {
      let errorMessage = 'Registration failed';
      
      if (error.response?.data) {
        // Handle different types of error responses
        if (typeof error.response.data === 'string') {
          errorMessage = error.response.data;
        } else if (error.response.data.detail) {
          errorMessage = error.response.data.detail;
        } else if (error.response.data.password) {
          errorMessage = error.response.data.password;
        } else if (error.response.data.username) {
          errorMessage = error.response.data.username;
        } else if (error.response.data.email) {
          errorMessage = error.response.data.email;
        } else if (typeof error.response.data === 'object') {
          // If it's an object, convert it to a readable string
          errorMessage = Object.values(error.response.data).join(', ');
        }
      }
      
      return {
        success: false,
        error: errorMessage,
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
    delete api.defaults.headers.common['Authorization'];
    setToken(null);
    setUser(null);
  };

  const refreshToken = async () => {
    try {
      const refresh = localStorage.getItem('refreshToken');
      if (!refresh) {
        logout();
        return false;
      }

      const response = await api.post('/auth/refresh/', {
        refresh,
      });

      const { access } = response.data;
      localStorage.setItem('token', access);
      api.defaults.headers.common['Authorization'] = `Bearer ${access}`;
      setToken(access);
      return true;
    } catch (error) {
      logout();
      return false;
    }
  };

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    refreshToken,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}; 
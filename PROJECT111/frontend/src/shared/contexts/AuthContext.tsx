import React, { createContext, useState, useContext, ReactNode, useEffect } from 'react';
import apiClient from '@/api';

// Define the User interface
interface User {
  user_id: number;
  email: string;
  name: string;
  is_profile_complete: boolean;
}

// Define the shape of the AuthContext
interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    // This effect runs once on app startup to check for existing tokens
    const checkAuthStatus = async () => {
      const accessToken = localStorage.getItem('accessToken');
      if (accessToken) {
        // Set the token in the API client for subsequent requests
        apiClient.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
        try {
          // Verify the token by fetching user info
          const response = await apiClient.get('/user-info/');
          if (response.status === 200 && response.data) {
            setUser(response.data);
            setIsAuthenticated(true);
          }
        } catch (error) {
          console.error("Session check failed, token might be expired.", error);
          // If token is invalid, clear it
          localStorage.removeItem('accessToken');
          localStorage.removeItem('refreshToken');
          delete apiClient.defaults.headers.common['Authorization'];
        }
      }
    };
    checkAuthStatus();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const response = await apiClient.post('/login/', { email, password });
      if (response.data.access && response.data.refresh) {
        const { access, refresh, user: userData } = response.data;

        // Store tokens in localStorage
        localStorage.setItem('accessToken', access);
        localStorage.setItem('refreshToken', refresh);

        // Set the Authorization header for future requests
        apiClient.defaults.headers.common['Authorization'] = `Bearer ${access}`;

        // Update auth state
        setUser(userData);
        setIsAuthenticated(true);
      }
    } catch (error) {
      console.error("Login failed:", error);
      // Re-throw the error to be handled by the calling component (e.g., display a message)
      throw error;
    }
  };

  const logout = () => {
    // Call backend logout if you have token blacklisting
    // apiClient.post('/logout/').catch(err => console.error("Logout API call failed", err));

    // Clear tokens and user state regardless of backend call success
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    delete apiClient.defaults.headers.common['Authorization'];
    setUser(null);
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
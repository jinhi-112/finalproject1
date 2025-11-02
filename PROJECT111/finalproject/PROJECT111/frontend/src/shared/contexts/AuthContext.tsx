import React, { createContext, useState, useContext, ReactNode, useEffect } from 'react';
import apiClient from '@/api';

// Define the User interface
interface User {
  user_id: number;
  email: string;
  name: string;
  is_profile_complete: boolean;
  // Add other user fields that you expect from the API
  [key: string]: any;
}

// Define the shape of the AuthContext
interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>; // Add refreshUser function
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [user, setUser] = useState<User | null>(null);

  const fetchAndSetUser = async () => {
    const accessToken = localStorage.getItem('accessToken');
    if (accessToken) {
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
      try {
        const response = await apiClient.get('/user-info/');
        if (response.status === 200 && response.data) {
          setUser(response.data);
          setIsAuthenticated(true);
          return response.data;
        }
      } catch (error) {
        console.error("Auth check failed, clearing tokens.", error);
        logout(); // Use logout function to clear state and tokens
      }
    }
    return null;
  };

  useEffect(() => {
    // This effect runs once on app startup to check for existing tokens
    fetchAndSetUser();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const response = await apiClient.post('/login/', { email, password });
      if (response.data.access && response.data.refresh) {
        const { access, refresh, user: userData } = response.data;

        localStorage.setItem('accessToken', access);
        localStorage.setItem('refreshToken', refresh);

        apiClient.defaults.headers.common['Authorization'] = `Bearer ${access}`;

        setUser(userData);
        setIsAuthenticated(true);
      }
    } catch (error) {
      console.error("Login failed:", error);
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    delete apiClient.defaults.headers.common['Authorization'];
    setUser(null);
    setIsAuthenticated(false);
  };

  const refreshUser = async () => {
    console.log("Refreshing user data...");
    await fetchAndSetUser();
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, logout, refreshUser }}>
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

import React, { createContext, useState, useContext, ReactNode, useEffect } from 'react';
import axios from 'axios';

interface User {
  user_id: number;
  email: string;
  name: string;
  is_profile_complete: boolean;
}

interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  login: (userData: User) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [user, setUser] = useState<User | null>(null);

  const checkAuth = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:8000/api/user-info/');
      if (response.status === 200 && response.data) {
        setUser(response.data);
        setIsAuthenticated(true);
      }
    } catch (error) {
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  useEffect(() => {
    checkAuth();
  }, []);

  const login = (userData: User) => {
    setUser(userData);
    setIsAuthenticated(true);
  };

  const logout = () => {
    axios.post('http://127.0.0.1:8000/api/logout/')
      .finally(() => {
        setUser(null);
        setIsAuthenticated(false);
      });
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

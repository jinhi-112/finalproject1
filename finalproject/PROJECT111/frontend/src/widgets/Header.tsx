import React, { useState, useEffect, useMemo, useRef } from 'react';
import { Link, useNavigate } from "react-router-dom";
import { Button } from "../shared/components/Button";
import { useAuth } from "../shared/contexts/AuthContext";
import { Bell } from 'lucide-react';
import { getNotifications, markNotificationAsRead } from '../api';
import { NotificationsDropdown } from '../features/notifications/components/NotificationsDropdown';

// Define type for a single notification
interface Notification {
  notification_id: number;
  message: string;
  notification_type: string;
  related_project: number | null;
  is_read: boolean;
  created_at: string;
}

export function Header() {
  const { isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const notificationRef = useRef<HTMLDivElement>(null);

  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  // Fetch notifications periodically
  useEffect(() => {
    if (!isAuthenticated) {
      setNotifications([]);
      return;
    }

    const fetchNotifications = async () => {
      try {
        const data = await getNotifications();
        setNotifications(data);
      } catch (error) {
        console.error("Failed to fetch notifications:", error);
      }
    };

    fetchNotifications(); // Initial fetch
    const intervalId = setInterval(fetchNotifications, 30000); // Poll every 30 seconds

    return () => clearInterval(intervalId); // Cleanup on unmount
  }, [isAuthenticated]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (notificationRef.current && !notificationRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const unreadCount = useMemo(() => {
    return notifications.filter(n => !n.is_read).length;
  }, [notifications]);

  const handleNotificationClick = async (notification: Notification) => {
    // Mark as read if it's not already
    if (!notification.is_read) {
      try {
        await markNotificationAsRead(notification.notification_id);
        // Update state locally for instant UI feedback
        setNotifications(prev => 
          prev.map(n => 
            n.notification_id === notification.notification_id ? { ...n, is_read: true } : n
          )
        );
      } catch (error) {
        console.error("Failed to mark notification as read:", error);
      }
    }

    // Navigate if there's a project to navigate to
    if (notification.related_project) {
      navigate(`/projects/${notification.related_project}`);
    }
    
    setIsDropdownOpen(false); // Close dropdown after click
  };

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white py-4 px-6 flex items-center border-b shadow-sm">
      {/* Left Section */}
      <div className="flex-1">
        <Link to="/" className="text-xl font-bold">AI 프로젝트 매칭</Link>
      </div>

      {/* Center Navigation */}
      <nav className="hidden md:flex gap-8">
        <Link to="/find-projects" className="text-sm font-medium text-gray-600 hover:text-gray-900">프로젝트 찾기</Link>
        {isAuthenticated && (
          <Link to="/recommended-projects" className="text-sm font-medium text-gray-600 hover:text-gray-900">AI 추천</Link>
        )}
        <Link to="/register-project" className="text-sm font-medium text-gray-600 hover:text-gray-900">프로젝트 등록</Link>
        {isAuthenticated && (
          <Link to="/project-management" className="text-sm font-medium text-gray-600 hover:text-gray-900">프로젝트 관리</Link>
        )}
        {/* <Link to="/about" className="text-sm font-medium text-gray-600 hover:text-gray-900">서비스 소개</Link>
        <Link to="/faq" className="text-sm font-medium text-gray-600 hover:text-gray-900">자주 묻는 질문</Link> */}
      </nav>

      {/* Right Section */}
      <div className="flex-1 flex justify-end">
        <div className="flex items-center gap-2">
          {isAuthenticated ? (
            <>
              <div className="relative" ref={notificationRef}>
                <button className="p-2 rounded-full hover:bg-gray-100 relative" onClick={() => setIsDropdownOpen(prev => !prev)}>
                  <Bell className="h-5 w-5" />
                  {unreadCount > 0 && (
                    <span className="absolute top-1 right-1 flex h-3 w-3">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
                    </span>
                  )}
                </button>
                {isDropdownOpen && (
                  <NotificationsDropdown 
                    notifications={notifications}
                    onNotificationClick={handleNotificationClick}
                  />
                )}
              </div>

              <Link to="/user-info">
                <Button variant="ghost">마이페이지</Button>
              </Link>
              <Button onClick={logout}>로그아웃</Button>
            </>
          ) : (
            <>
              <Link to="/login">
                <Button variant="ghost">로그인</Button>
              </Link>
              <Link to="/register">
                <Button>회원가입</Button>
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}

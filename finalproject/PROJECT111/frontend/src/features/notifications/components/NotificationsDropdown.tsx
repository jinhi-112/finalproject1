import React from 'react';
import { useNavigate } from 'react-router-dom';

// Define types
interface Notification {
  notification_id: number;
  message: string;
  notification_type: string;
  related_project: number | null;
  is_read: boolean;
  created_at: string;
}

interface NotificationsDropdownProps {
  notifications: Notification[];
  onNotificationClick: (notification: Notification) => void;
}

// Helper to format time since notification
const timeSince = (date: string) => {
  const seconds = Math.floor((new Date().getTime() - new Date(date).getTime()) / 1000);
  let interval = seconds / 31536000;
  if (interval > 1) return Math.floor(interval) + "년 전";
  interval = seconds / 2592000;
  if (interval > 1) return Math.floor(interval) + "달 전";
  interval = seconds / 86400;
  if (interval > 1) return Math.floor(interval) + "일 전";
  interval = seconds / 3600;
  if (interval > 1) return Math.floor(interval) + "시간 전";
  interval = seconds / 60;
  if (interval > 1) return Math.floor(interval) + "분 전";
  return Math.floor(seconds) + "초 전";
};

export const NotificationsDropdown: React.FC<NotificationsDropdownProps> = ({ notifications, onNotificationClick }) => {
  return (
    <div className="absolute top-full right-0 mt-2 w-80 bg-white rounded-md shadow-lg border z-50">
      <div className="p-4 font-bold border-b">알림</div>
      <div className="max-h-96 overflow-y-auto">
        {notifications.length === 0 ? (
          <p className="text-center text-gray-500 py-6">새로운 알림이 없습니다.</p>
        ) : (
          notifications.map((notif) => (
            <div
              key={notif.notification_id}
              onClick={() => onNotificationClick(notif)}
              className={`p-4 border-b border-gray-100 cursor-pointer hover:bg-gray-50 ${!notif.is_read ? 'bg-blue-50' : ''}`}
            >
              <div className="flex items-start">
                <div className={`mt-1.5 mr-3 w-2 h-2 rounded-full flex-shrink-0 ${!notif.is_read ? 'bg-blue-500' : 'bg-transparent'}`}></div>
                <div className="flex-1">
                  <p className="text-sm text-gray-800">{notif.message}</p>
                  <p className="text-xs text-gray-400 mt-1">{timeSince(notif.created_at)}</p>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

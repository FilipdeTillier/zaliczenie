import { ChatWindow } from "../ChatWindow/ChatWindow";
import { ConversationsList } from "../ConversationsList/ConversationsList";
// import { LogOut, User } from 'lucide-react';
// import { useAppSelector } from '../../hooks/useAppSelector';
// import { useAppDispatch } from '../../hooks/useAppDispatch';
// import { logout } from '../../store/authSlice';
// import { ConversationsList } from "../ConversationsList/ConversationsList";
import React from "react";

export const AppLayout: React.FC = () => {
  // const dispatch = useAppDispatch();
  // const { user } = useAppSelector(state => state.auth);

  // const handleLogout = () => {
  //   dispatch(logout());
  // };

  return (
    <div className="flex h-screen bg-gray-50">
      <div className="w-80 bg-white border-r border-gray-200 flex-shrink-0">
        {/* <div className="p-4 border-b border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {user?.avatar ? (
                <img
                  src={user.avatar}
                  alt={user.name}
                  className="w-8 h-8 rounded-full object-cover"
                />
              ) : (
                <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                  <User className="w-4 h-4 text-white" />
                </div>
              )}
              <div>
                <p className="text-sm font-medium text-gray-900">{user?.name}</p>
                <p className="text-xs text-gray-500">{user?.email}</p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors duration-200"
              title="Logout"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div> */}
        <ConversationsList />
      </div>

      <div className="flex-1 flex flex-col">
        <ChatWindow />
      </div>
    </div>
  );
};

import { Clock, MessageSquare, Plus } from "lucide-react";
import {
  createConversation,
  setActiveConversation,
} from "../../store/chatSlice";

import type { Conversation } from "../../types";
import React from "react";
import { useAppDispatch } from "../../hooks/useAppDispatch";
import { useAppSelector } from "../../hooks/useAppSelector";

export const ConversationsList: React.FC = () => {
  const dispatch = useAppDispatch();
  const { conversations, activeConversationId } = useAppSelector(
    (state) => state.chat
  );

  const handleCreateNewConversation = () => {
    const newConversation: Conversation = {
      id: Date.now().toString(),
      title: "New Conversation",
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    dispatch(createConversation(newConversation));
  };

  const handleSelectConversation = (conversationId: string) => {
    dispatch(setActiveConversation(conversationId));
  };

  const formatTimestamp = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) {
      return date.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      });
    } else if (days === 1) {
      return "Yesterday";
    } else if (days < 7) {
      return `${days} days ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <button
          onClick={handleCreateNewConversation}
          className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors duration-200"
        >
          <Plus className="w-4 h-4" />
          New Chat
        </button>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto">
        {conversations.length === 0 ? (
          <div className="p-4 text-center text-gray-500">
            <MessageSquare className="w-12 h-12 mx-auto mb-3 text-gray-300" />
            <p className="text-sm">No conversations yet</p>
            <p className="text-xs text-gray-400 mt-1">
              Start a new chat to begin
            </p>
          </div>
        ) : (
          <div className="p-2 space-y-1">
            {conversations.map((conversation) => (
              <button
                key={conversation.id}
                onClick={() => handleSelectConversation(conversation.id)}
                className={`w-full p-3 text-left rounded-lg transition-all duration-200 group ${
                  activeConversationId === conversation.id
                    ? "bg-blue-50 border border-blue-200"
                    : "hover:bg-gray-50 border border-transparent"
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {conversation.title}
                    </p>
                    {conversation.messages.length > 0 && (
                      <p className="text-xs text-gray-500 mt-1 truncate">
                        {
                          conversation.messages[
                            conversation.messages.length - 1
                          ].content
                        }
                      </p>
                    )}
                  </div>
                  <div className="flex items-center ml-2 text-xs text-gray-400">
                    <Clock className="w-3 h-3 mr-1" />
                    {formatTimestamp(conversation.updatedAt)}
                  </div>
                </div>
                <div className="flex items-center justify-between mt-2">
                  <span className="text-xs text-gray-400">
                    {conversation.messages.length} messages
                  </span>
                  {activeConversationId === conversation.id && (
                    <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                  )}
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

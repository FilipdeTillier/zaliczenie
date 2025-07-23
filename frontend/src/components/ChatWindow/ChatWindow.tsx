import { Bot, Sparkles, User } from "lucide-react";
import React, { useEffect, useRef } from "react";

import { ChatHeader } from "../atoms/ChatHeader/ChatHeader";
import { ChatMessage } from "../atoms/ChatMessage/ChatMessage";
import { MessageInput } from "../MessageInput/MessageInput";
import { useAppSelector } from "../../hooks/useAppSelector";

export const ChatWindow: React.FC = () => {
  const { conversations, activeConversationId, isLoading } = useAppSelector(
    (state) => state.chat
  );
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const activeConversation = conversations.find(
    (c) => c.id === activeConversationId
  );

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [activeConversation?.messages]);

  const formatTimestamp = (date: Date) => {
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  if (!activeConversation) {
    return (
      <div className="flex-1 flex flex-col">
        {/* Empty State */}
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center max-w-md mx-auto p-8">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <Sparkles className="w-8 h-8 text-blue-600" />
            </div>
            <h2 className="text-2xl font-semibold text-gray-900 mb-3">
              Welcome to AI Chat
            </h2>
            <p className="text-gray-600 mb-6">
              Start a new conversation to begin chatting with AI. Select a
              model, enable RAG if needed, and attach files to enhance your
              experience.
            </p>
          </div>
        </div>
        <MessageInput />
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col">
      <ChatHeader
        title={activeConversation.title}
        messageCount={activeConversation.messages.length}
        updatedAt={activeConversation.updatedAt}
      />

      <div className="flex-1 overflow-y-auto bg-gray-50">
        {activeConversation.messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="w-12 h-12 bg-gray-200 rounded-full flex items-center justify-center mx-auto mb-3">
                <Bot className="w-6 h-6 text-gray-500" />
              </div>
              <p className="text-gray-500 text-sm">Start the conversation</p>
            </div>
          </div>
        ) : (
          <div className="max-w-4xl mx-auto p-4 space-y-6">
            {activeConversation.messages.map((message) => (
              <ChatMessage message={message} />
            ))}
            {isLoading && (
              <div className="flex gap-4">
                <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0">
                  <Bot className="w-4 h-4 text-white" />
                </div>
                <div className="bg-white shadow-sm border border-gray-200 p-4 rounded-2xl">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div
                      className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                      style={{ animationDelay: "0.1s" }}
                    ></div>
                    <div
                      className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                      style={{ animationDelay: "0.2s" }}
                    ></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      <MessageInput />
    </div>
  );
};

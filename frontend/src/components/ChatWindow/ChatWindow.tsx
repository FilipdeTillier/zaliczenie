import React, { useEffect, useRef } from "react";

import { Bot } from "lucide-react";
import ChatEmptyState from "../atoms/ChatEmptyState/ChatEmptyState";
import { ChatHeader } from "../atoms/ChatHeader/ChatHeader";
import ChatLoading from "../atoms/ChatLoading/ChatLoading";
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

  if (!activeConversation) {
    return (
      <div className="flex-1 flex flex-col">
        <ChatEmptyState />
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
            {isLoading && <ChatLoading />}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      <MessageInput />
    </div>
  );
};

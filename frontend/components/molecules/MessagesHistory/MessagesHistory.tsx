import React, { useEffect, useRef } from "react";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

interface MessagesHistoryProps {
  messages: Message[];
}

export const MessagesHistory: React.FC<MessagesHistoryProps> = ({
  messages,
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.map((message, index) => (
        <div
          key={index}
          className={`flex ${
            message.role === "user" ? "justify-end" : "justify-start"
          }`}
        >
          <div
            className={`max-w-[70%] rounded-lg p-3 ${
              message.role === "user"
                ? "bg-blue-500 text-black"
                : "bg-gray-100 text-gray-800"
            }`}
          >
            <p className="text-sm text-black">{message.content}</p>
            <p className="text-xs text-black mt-1 opacity-70">
              {message.timestamp}
            </p>
          </div>
        </div>
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
};

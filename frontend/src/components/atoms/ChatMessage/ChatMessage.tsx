import { Bot, User } from "lucide-react";

import { FormattedText } from "../../../helpers/textFormatter.tsx";
import type { Message } from "../../../types";
import React from "react";

interface ChatMessageProps {
  message: Message;
}

const formatTimestamp = (date: Date) => {
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
};

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  return (
    <div
      key={message.id}
      className={`flex gap-4 ${
        message.role === "user" ? "justify-end" : "justify-start"
      }`}
    >
      {message.role === "assistant" && (
        <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0">
          <Bot className="w-4 h-4 text-white" />
        </div>
      )}
      <div
        className={`max-w-3xl ${message.role === "user" ? "order-first" : ""}`}
      >
        <div
          className={`p-4 rounded-2xl ${
            message.role === "user"
              ? "bg-blue-600 text-white ml-12"
              : "bg-white shadow-sm border border-gray-200"
          }`}
        >
          <FormattedText text={message.content} />
        </div>
        <p
          className={`text-xs text-gray-500 mt-2 ${
            message.role === "user" ? "text-right" : "text-left"
          }`}
        >
          {formatTimestamp(message.timestamp)}
        </p>
      </div>
      {message.role === "user" && (
        <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center flex-shrink-0">
          <User className="w-4 h-4 text-white" />
        </div>
      )}
    </div>
  );
};

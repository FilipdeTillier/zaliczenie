import { Bot } from "lucide-react";
import React from "react";

export const ChatLoading: React.FC = () => (
  <div
    className="flex gap-4"
    role="status"
    aria-live="polite"
    aria-label="AI is typing"
  >
    <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0">
      <Bot className="w-4 h-4 text-white" aria-hidden="true" />
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
);

export default ChatLoading;

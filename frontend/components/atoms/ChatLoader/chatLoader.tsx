import React from "react";

interface ChatLoaderProps {
  className?: string;
}

export const ChatLoader: React.FC<ChatLoaderProps> = ({ className = "" }) => {
  return (
    <div className={`flex justify-start ${className}`}>
      <div className="max-w-[70%] rounded-lg p-3 bg-gray-100">
        <div className="flex items-center space-x-1">
          <div
            className="w-2 h-2 bg-gray-600 rounded-full animate-bounce"
            style={{ animationDelay: "0ms" }}
          ></div>
          <div
            className="w-2 h-2 bg-gray-600 rounded-full animate-bounce"
            style={{ animationDelay: "150ms" }}
          ></div>
          <div
            className="w-2 h-2 bg-gray-600 rounded-full animate-bounce"
            style={{ animationDelay: "300ms" }}
          ></div>
        </div>
      </div>
    </div>
  );
};

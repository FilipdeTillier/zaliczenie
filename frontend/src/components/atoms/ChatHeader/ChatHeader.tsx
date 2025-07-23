import React from "react";

interface ChatHeaderProps {
  title: string;
  messageCount: number;
  updatedAt: Date;
}

const formatTimestamp = (date: Date) => {
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
};

export const ChatHeader: React.FC<ChatHeaderProps> = ({
  title,
  messageCount,
  updatedAt,
}) => (
  <div className="bg-white border-b border-gray-200 p-4">
    <h1 className="text-lg font-semibold text-gray-900">{title}</h1>
    <p className="text-sm text-gray-500">
      {messageCount} messages • Last updated {formatTimestamp(updatedAt)}
    </p>
  </div>
);

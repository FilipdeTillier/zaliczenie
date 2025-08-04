import React from "react";
import { Sparkles } from "lucide-react";

export const ChatEmptyState: React.FC = () => (
  <div className="flex-1 flex items-center justify-center">
    <div className="text-center max-w-md mx-auto p-8">
      <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
        <Sparkles className="w-8 h-8 text-blue-600" />
      </div>
      <h2 className="text-2xl font-semibold text-gray-900 mb-3">
        Welcome to AI Chat
      </h2>
      <p className="text-gray-600 mb-6">
        Start a new conversation to begin chatting with AI. Select a model,
        enable RAG if needed, and attach files to enhance your experience.
      </p>
    </div>
  </div>
);

export default ChatEmptyState;

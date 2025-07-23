import type { ChatPayload, Message } from "../types/chat.types";
import { useCallback, useState } from "react";

interface UseModelResult {
  isLoading: boolean;
  messages: Message[];
  sendMessage: (payload: ChatPayload) => Promise<void>;
}

export function useModel(): UseModelResult {
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);

  const sendMessage = useCallback(async (payload: ChatPayload) => {
    setIsLoading(true);
    try {
      const userMessages: Message[] = payload.messages.map((msg) => ({
        ...msg,
        timestamp: new Date().toLocaleTimeString(),
      }));
      setMessages((prev) => [...prev, ...userMessages]);

      const endpoint = payload.useLocal ? "/api/local-llm" : "/api/openai-chat";

      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error("Failed to send message");
      }

      const data = await response.json();

      const assistantMessages: Message[] = Array.isArray(data) ? data : [data];

      setMessages((prev) => [
        ...prev,
        ...assistantMessages.map((msg) => ({
          ...msg,
          role: msg.role || "assistant",
          timestamp: msg.timestamp || new Date().toLocaleTimeString(),
        })),
      ]);
    } catch (error) {
      console.error("Error sending message:", error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    isLoading,
    messages,
    sendMessage,
  };
}

import { Button, ButtonVarinat } from "../button";
import React, { useCallback, useEffect, useRef, useState } from "react";

import { MessagesHistory } from "../MessagesHistory";
import { ModelDropdown } from "..//modelDropdown/modelDropdown";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

const ChatWindow: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleModelChange = useCallback((model: string) => {
    // Handle model change here
    console.log("Selected model:", model);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    const newMessage: Message = {
      role: "user",
      content: inputMessage,
      timestamp: new Date().toLocaleTimeString(),
    };

    setMessages((prev) => [...prev, newMessage]);
    setInputMessage("");

    const body = {
      query: {
        model: "gemma3:1b",
        stream: false,
        messages: [...messages, newMessage],
      },
      use_local: true,
      use_rag: false,
    };

    try {
      const response = await fetch("http://localhost:8080/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      });

      if (!response.ok) throw new Error("Failed to send message");

      const data = await response.json();

      const assistantMessage: Message = {
        role: "assistant",
        content: data.response.choices[0].message.content,
        timestamp: new Date().toLocaleTimeString(),
      };

      setMessages((prev) => {
        console.log(prev, assistantMessage);
        return [...prev, assistantMessage];
      });
    } catch (error) {
      console.error("Error sending message:", error);
    }
  };

  return (
    <div className="flex flex-col h-[80vh] w-full max-w-4xl mx-auto bg-white rounded-lg shadow-lg">
      <MessagesHistory messages={messages} />

      <form onSubmit={handleSubmit} className="border-t p-4">
        <div className="flex space-x-2">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
            placeholder="Type your message..."
            className="flex-1 p-2 border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={2}
          />

          <ModelDropdown
            onModelChanged={handleModelChange}
            currentModel="deepseek-r1:7b" // Optional: set current model
          />

          <Button type="submit" variant={ButtonVarinat.primary}>
            Send
          </Button>
        </div>
      </form>
    </div>
  );
};

export default ChatWindow;

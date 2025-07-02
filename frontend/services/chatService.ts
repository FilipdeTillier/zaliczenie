import { ChatPayload, Message } from "../types/chat.types";

export const postMessage = async (body: ChatPayload): Promise<Message> => {
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

  return assistantMessage;
};

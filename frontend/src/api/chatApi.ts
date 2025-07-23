import type { Message } from "../types";
import { postToOpenAIChat } from "../services/chatService";
import { useMutation } from "@tanstack/react-query";

interface SendMessageRequest {
  message: Message[];
  model: string;
  useRag: boolean;
  conversationId?: string;
  attachedFiles?: File[];
}

interface SendMessageResponse {
  id: string;
  content: string;
  role: "assistant";
  timestamp: Date;
}

const sendMessage = async (
  data: SendMessageRequest
): Promise<SendMessageResponse> => {
  const response = await postToOpenAIChat(data.message, data.model);

  return response;
};

export const useSendMessage = () => {
  return useMutation({
    mutationFn: sendMessage,
  });
};

import type { ChatRequest, Message } from "../types/chat.types";

import type { OllamaResponse } from "../types/ollamaResponse";
import axios from "axios";

export const postLocalLLMMessageService = async (
  dataForm: ChatRequest
): Promise<Message> => {
  try {
    const response = await axios.post<{ response: OllamaResponse }>(
      "http://localhost:8080/query",
      dataForm
    );

    const { data } = response;

    const assistantMessage: Message = {
      role: "assistant",
      content: data.response.message.content,
      timestamp: new Date().toLocaleTimeString(),
    };

    return assistantMessage;
  } catch (err) {
    throw Error(err);
  }
};

export const streamFromOllama = async (dataForm: ChatRequest) => {
  const response = await axios.post<{ response: OllamaResponse }>(
    "http://localhost:8080/query",
    dataForm
  );

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();

    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split("\n");

    for (const line of lines) {
      if (line.trim()) {
        try {
          const data = JSON.parse(line);
          if (data.response) {
            console.log(data.response);
          }
        } catch (e) {
          // Ignoruj błędy parsowania
        }
      }
    }
  }
};

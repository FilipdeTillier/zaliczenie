import { ChatPayload, ChatRequest } from "../types/chat.types";

import type { OpenAIResponse } from "../types/openaiResponse";

export const mapPayload = ({
  selectedModel,
  stream,
  inputMessage,
  collectionName,
  useLocal,
  useRag,
}: ChatPayload): ChatRequest => {
  return {
    query: {
      model: selectedModel,
      stream: stream,
      messages: inputMessage,
    },
    // collection_name: collectionName,
    use_rag: useRag,
    use_local: useLocal,
  };
};

export const mapOpenAiResponse = (response: OpenAIResponse) => {
  if (!response || !Array.isArray(response.output)) return [];

  return response.output.map((msg) => {
    const contentItem = Array.isArray(msg.content)
      ? msg.content.find((c: any) => c.type === "output_text")
      : null;

    return {
      role: msg.role || "assistant",
      content: contentItem ? contentItem.text : "",
      timestamp: new Date().toLocaleTimeString(),
    };
  })[0];
};

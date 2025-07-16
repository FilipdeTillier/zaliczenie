import { ChatPayload, ChatRequest } from "../types/chat.types";

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

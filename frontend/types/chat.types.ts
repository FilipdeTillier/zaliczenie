export type Message = {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
};

export type ChatPayload = {
  query: {
    model: string;
    stream: boolean;
    messages: Message[];
  };
  use_rag: boolean;
};

import { z } from "zod";

export const MessageSchema = z.object({
  role: z.enum(["user", "assistant"]),
  content: z.string(),
  timestamp: z.string(),
});

export const QuerySchema = z.object({
  model: z.string(),
  stream: z.boolean(),
  messages: z.array(MessageSchema),
});

export const ChatPayloadSchema = z.object({
  inputMessage: z.array(MessageSchema),
  selectedModel: z.string(),
  useLocal: z.boolean(),
  stream: z.boolean(),
  collectionName: z.string(),
  useRag: z.boolean(),
});

export const ChatRequestSchema = z.object({
  query: QuerySchema,
  collection_name: z.string().optional(),
  use_rag: z.boolean(),
  use_local: z.boolean(),
});

export type Message = z.infer<typeof MessageSchema>;
export type Query = z.infer<typeof QuerySchema>;
export type ChatRequest = z.infer<typeof ChatRequestSchema>;
export type ChatPayload = z.infer<typeof ChatPayloadSchema>;

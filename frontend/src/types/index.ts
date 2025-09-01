import type { DocumentItem } from "../services/documentsService";
import { z } from "zod";

export const MessageSchema = z.object({
  id: z.string(),
  content: z.string(),
  role: z.enum(["user", "assistant"]),
  timestamp: z.date(),
});

export const ConversationSchema = z.object({
  id: z.string(),
  title: z.string(),
  messages: z.array(MessageSchema),
  createdAt: z.date(),
  updatedAt: z.date(),
});

export const ChatFormSchema = z.object({
  message: z.string().min(1, "Message cannot be empty"),
  model: z.string(),
  useRag: z.boolean(),
  attachedFiles: z.array(
    z.object({
      name: z.string(),
      type: z.enum(["pdf", "docx", "xlsx"]),
      size: z.number(),
    })
  ),
});

export type Message = z.infer<typeof MessageSchema>;
export type Conversation = z.infer<typeof ConversationSchema>;
export type ChatFormData = z.infer<typeof ChatFormSchema>;

export interface ChatState {
  conversations: Conversation[];
  activeConversationId: string | null;
  isLoading: boolean;
  documents: DocumentItem[];
}

export interface FileAttachment {
  name: string;
  type: "pdf" | "docx" | "xlsx";
  size: number;
  file: File;
}

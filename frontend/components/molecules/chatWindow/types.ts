import { MessageSchema } from "../../../types/chat.types";
import { z } from "zod";

export const ChatWindowFormSchema = z.object({
  model: z.string(),
  stream: z.boolean(),
  messages: z.array(MessageSchema),
  collection_name: z.string(),
  use_local: z.boolean(),
  use_rag: z.boolean(),
});

export type ChatWindowFormZod = z.infer<typeof ChatWindowFormSchema>;

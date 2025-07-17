import { z } from "zod";

export const OllamaMessageSchema = z.object({
  role: z.string(),
  content: z.string(),
});

export const OllamaResponseSchema = z.object({
  model: z.string(),
  created_at: z.string(),
  message: OllamaMessageSchema,
  done_reason: z.string(),
  done: z.boolean(),
  total_duration: z.number(),
  load_duration: z.number(),
  prompt_eval_count: z.number(),
  prompt_eval_duration: z.number(),
  eval_count: z.number(),
  eval_duration: z.number(),
});

export type OllamaMessage = z.infer<typeof OllamaMessageSchema>;

export type OllamaResponse = z.infer<typeof OllamaResponseSchema>;

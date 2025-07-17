export type OpenAIContentItem = {
  type: string;
  annotations?: any[];
  logprobs?: any[];
  text?: string;
};

export type OpenAIOutputMessage = {
  id: string;
  type: string;
  status: string;
  content: OpenAIContentItem[];
  role: string;
};

export type OpenAIReasoning = {
  effort?: any;
  summary?: any;
};

export type OpenAITextFormat = {
  type: string;
};

export type OpenAIText = {
  format: OpenAITextFormat;
};

export type OpenAIUsageDetails = {
  cached_tokens?: number;
};

export type OpenAIOutputTokensDetails = {
  reasoning_tokens?: number;
};

export type OpenAIUsage = {
  input_tokens: number;
  input_tokens_details?: OpenAIUsageDetails;
  output_tokens: number;
  output_tokens_details?: OpenAIOutputTokensDetails;
  total_tokens: number;
};

export type OpenAIResponse = {
  id: string;
  object: string;
  created_at: number;
  status: string;
  background?: boolean;
  error?: any;
  incomplete_details?: any;
  instructions?: any;
  max_output_tokens?: any;
  max_tool_calls?: any;
  model: string;
  output: OpenAIOutputMessage[];
  parallel_tool_calls?: boolean;
  previous_response_id?: string | null;
  reasoning?: OpenAIReasoning;
  service_tier?: string;
  store?: boolean;
  temperature?: number;
  text?: OpenAIText;
  tool_choice?: string;
  tools?: any[];
  top_logprobs?: number;
  top_p?: number;
  truncation?: string;
  usage?: OpenAIUsage;
  user?: any;
  metadata?: { [key: string]: any };
};

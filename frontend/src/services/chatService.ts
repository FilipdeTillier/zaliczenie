import type { ChatRequest } from "../types/chat.types";
import type { Message } from "../types";
import type { OllamaResponse } from "../types/ollamaResponse";
import axios from "axios";
import { mapOpenAiResponse } from "../helpers/payloadMapper";

export const postLocalLLMMessageService = async (dataForm: ChatRequest) => {
  // try {
  //   const response = await axios.post<{ response: OllamaResponse }>(
  //     "http://localhost:8080/query",
  //     dataForm
  //   );
  //   const { data } = response;
  //   const assistantMessage: Message = {
  //     role: "assistant",
  //     content: data.response.message.content,
  //     timestamp: new Date().toLocaleTimeString(),
  //   };
  //   return assistantMessage;
  // } catch (err) {
  //   throw Error(err);
  // }
};

export const postToOpenAIChat = async (
  messages: Message[],
  model: string = "gpt-3.5-turbo"
) => {
  try {
    const dataForm = {
      model,
      messages,
    };
    const { data } = await axios.post(
      "http://localhost:8080/open_ai/chat",
      dataForm
    );
    const mapReponse = mapOpenAiResponse(data.response);
    return mapReponse;
  } catch (err) {
    throw Error(err);
  }
};

import { Button, ButtonVarinat } from "../../atoms/Button";
import type { ChatPayload, Message } from "../../../types/chat.types";
import React, { useCallback, useEffect, useRef, useState } from "react";
import {
  postLocalLLMMessageService,
  postToOpenAIChat,
} from "../../../services/chatService";

import { ChatLoader } from "../../atoms/ChatLoader/chatLoader";
import { Checkbox } from "../../atoms/Checkbox/checkbox";
import { MessagesHistory } from "../MessagesHistory";
import { ModelDropdown } from "../ModelDropdown/modelDropdown";
import { Textarea } from "../../atoms/Textarea/textarea";
import { mapPayload } from "../../../helpers/payloadMapper";
import { useFormik } from "formik";

const formikInitialValues: ChatPayload = {
  message: [],
  model: "",
  useLocal: true,
  stream: false,
  collectionName: "string",
  useRag: false,
};

const ChatWindow: React.FC = () => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [messagesHistory, setMessagesHistory] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const onSubmit = async (values: ChatPayload) => {
    if (!values.message.length) return;

    const newUserMessage = values.message[0];

    setMessagesHistory((prev) => [...prev, newUserMessage]);

    setIsLoading(true);

    try {
      const payload = mapPayload({
        ...values,
        message: [...messagesHistory, newUserMessage],
      });

      formik.setFieldValue("message", []);

      let response;
      if (values.useLocal) {
        response = await postLocalLLMMessageService(payload);
      } else {
        response = await postToOpenAIChat(
          payload.query.messages,
          "gpt-3.5-turbo"
        );
      }

      console.log(response);

      setMessagesHistory([
        ...messagesHistory,
        ...payload.query.messages.slice(messagesHistory.length),
        response,
      ]);
    } catch (error) {
      console.error("Error sending message:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const formik = useFormik<ChatPayload>({
    initialValues: formikInitialValues,
    onSubmit,
    validate: () => ({}),
  });

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [formik.values.message, isLoading]);

  const handleModelChange = useCallback(
    (model: string) => {
      formik.setFieldValue("model", model);
      console.log("Selected model:", model);
    },
    [formik]
  );

  return (
    <div className="flex flex-col h-[80vh] w-full max-w-4xl mx-auto bg-white rounded-lg shadow-lg">
      <MessagesHistory messages={messagesHistory} />
      {isLoading && <ChatLoader className="p-4" />}
      <form onSubmit={formik.handleSubmit} className="border-t p-4">
        <div className="flex space-x-2 items-center">
          <Textarea
            name="message"
            value={formik.values.message
              .map((msg: { role: string; content: string }) => msg.content)
              .join("\n")}
            onChange={(e) => {
              const lines = e.target.value
                .split("\n")
                .filter((line) => line.trim() !== "");
              const messages = lines.map((line) => ({
                role: "user",
                content: line,
                timestamp: new Date().toLocaleTimeString(),
              }));
              formik.setFieldValue("message", messages);
            }}
            onBlur={formik.handleBlur}
            placeholder="Type your message..."
            error={
              formik.touched.message && formik.errors.message
                ? (formik.errors.message as string)
                : undefined
            }
            rows={2}
            className="flex-1"
          />
          <ModelDropdown
            onModelChanged={handleModelChange}
            currentModel={formik.values.model}
          />
          <div className="flex items-center space-x-2">
            <Checkbox
              name="stream"
              label=""
              spanText="Stream"
              checked={formik.values.stream}
              onChange={() =>
                formik.setFieldValue("stream", !formik.values.stream)
              }
              onBlur={formik.handleBlur}
              error={
                formik.touched.stream && formik.errors.stream
                  ? (formik.errors.stream as string)
                  : undefined
              }
            />
            <Checkbox
              name="useLocal"
              label=""
              spanText="Local"
              checked={formik.values.useLocal}
              onChange={() =>
                formik.setFieldValue("useLocal", !formik.values.useLocal)
              }
              onBlur={formik.handleBlur}
              error={
                formik.touched.useLocal && formik.errors.useLocal
                  ? (formik.errors.useLocal as string)
                  : undefined
              }
            />
          </div>
          <Button type="submit" variant={ButtonVarinat.primary}>
            Send
          </Button>
        </div>
      </form>
    </div>
  );
};

export default ChatWindow;

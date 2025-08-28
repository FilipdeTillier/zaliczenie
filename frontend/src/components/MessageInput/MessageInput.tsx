import * as Yup from "yup";

import type {
  ChatFormData,
  Conversation,
  FileAttachment,
  Message,
} from "../../types";
import { Field, Form, Formik, type FormikHelpers } from "formik";
import { Paperclip, Send, Settings, Zap, FileText } from "lucide-react";
import React, { useState } from "react";
import {
  addMessage,
  createConversation,
  setLoading,
  updateConversationTitle,
} from "../../store/chatSlice";

import { FileAttachmentModal } from "../FileAttachmentModal/FileAttachmentModal";
import { DocumentsModal } from "../DocumentsModal/DocumentsModal";
import { useAppDispatch } from "../../hooks/useAppDispatch";
import { useAppSelector } from "../../hooks/useAppSelector";
import { useSendMessage } from "../../api/chatApi";

const validationSchema = Yup.object({
  message: Yup.string()
    .required("Message is required")
    .min(1, "Message cannot be empty"),
  model: Yup.string().required("Model is required"),
  useRag: Yup.boolean(),
});

const models = [
  { value: "gpt-4", label: "GPT-4" },
  { value: "gpt-3.5-turbo", label: "GPT-3.5 Turbo" },
  { value: "claude-3", label: "Claude 3" },
  { value: "gemini-pro", label: "Gemini Pro" },
];

export const MessageInput: React.FC = () => {
  const dispatch = useAppDispatch();
  const { activeConversationId, conversations, isLoading, documents } =
    useAppSelector((state) => state.chat);
  const sendMessageMutation = useSendMessage();

  const [isFileModalOpen, setIsFileModalOpen] = useState(false);
  const [attachedFiles, setAttachedFiles] = useState<FileAttachment[]>([]);
  const [isDocumentsModalOpen, setIsDocumentsModalOpen] = useState(false);

  const initialValues: Omit<ChatFormData, "attachedFiles"> = {
    message: "",
    model: "gpt-3.5-turbo",
    useRag: false,
  };

  const handleSubmit = async (
    values: typeof initialValues,
    { resetForm }: FormikHelpers<typeof initialValues>
  ) => {
    if (!values.message.trim()) return;

    let conversationId = activeConversationId;

    if (!conversationId) {
      const newConversation: Conversation = {
        id: Date.now().toString(),
        title:
          values.message.slice(0, 50) +
          (values.message.length > 50 ? "..." : ""),
        messages: [],
        createdAt: new Date(),
        updatedAt: new Date(),
      };
      dispatch(createConversation(newConversation));
      conversationId = newConversation.id;
    }

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      content: values.message,
      role: "user",
      timestamp: new Date(),
    };

    dispatch(addMessage({ conversationId, message: userMessage }));

    // Update conversation title if it's still "New Conversation"
    const conversation = conversations.find((c) => c.id === conversationId);
    if (conversation?.title === "New Conversation") {
      const title =
        values.message.slice(0, 50) + (values.message.length > 50 ? "..." : "");
      dispatch(updateConversationTitle({ id: conversationId, title }));
    }

    dispatch(setLoading(true));

    const prevMessages = conversation?.messages || [];

    const currentMessage: Message = {
      id: "string",
      content: values.message,
      role: "user",
      timestamp: new Date(),
    };

    try {
      const response = await sendMessageMutation.mutateAsync({
        message: [...prevMessages, currentMessage],
        model: values.model,
        useRag: values.useRag,
        conversationId,
        attachedFiles: attachedFiles.map((f) => f.file),
        documents: documents,
      });

      const assistantMessage: Message = {
        ...response,
        timestamp: new Date(response.timestamp),
      };

      dispatch(addMessage({ conversationId, message: assistantMessage }));
      resetForm();
      setAttachedFiles([]);
    } catch (error) {
      console.error("Failed to send message:", error);
    } finally {
      dispatch(setLoading(false));
    }
  };

  const handleFileAttachment = (files: FileAttachment[]) => {
    setAttachedFiles(files);
  };

  return (
    <div className="bg-white border-t border-gray-200 p-4">
      <Formik
        initialValues={initialValues}
        validationSchema={validationSchema}
        onSubmit={handleSubmit}
      >
        {({ values, isValid }) => (
          <Form>
            {/* Controls Row */}
            <div className="flex items-center gap-4 mb-3 pb-3 border-b border-gray-100">
              {/* Model Selection */}
              <div className="flex items-center gap-2">
                <Settings className="w-4 h-4 text-gray-500" />
                <Field
                  as="select"
                  name="model"
                  className="text-sm bg-gray-50 border border-gray-300 rounded-lg px-3 py-1.5 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {models.map((model) => (
                    <option key={model.value} value={model.value}>
                      {model.label}
                    </option>
                  ))}
                </Field>
              </div>

              {/* RAG Toggle */}
              <div className="flex items-center gap-2">
                <Zap className="w-4 h-4 text-gray-500" />
                <label className="flex items-center gap-2 text-sm text-gray-700">
                  <Field
                    type="checkbox"
                    name="useRag"
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  Use RAG
                </label>
              </div>

              {/* File Attachment */}
              <button
                type="button"
                onClick={() => setIsFileModalOpen(true)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm transition-colors duration-200 ${
                  attachedFiles.length > 0
                    ? "bg-blue-100 text-blue-700 border border-blue-200"
                    : "bg-gray-50 text-gray-700 border border-gray-300 hover:bg-gray-100"
                }`}
              >
                <Paperclip className="w-4 h-4" />
                {attachedFiles.length > 0
                  ? `${attachedFiles.length} file(s)`
                  : "Attach"}
              </button>

              {/* Browse Saved Documents */}
              <button
                type="button"
                onClick={() => setIsDocumentsModalOpen(true)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm transition-colors duration-200 ${
                  documents.length > 0
                    ? "bg-blue-100 text-blue-700 border border-blue-200"
                    : "bg-gray-50 text-gray-700 border border-gray-300 hover:bg-gray-100"
                }`}
              >
                <FileText className="w-4 h-4" />
                {documents.length > 0 ? `${documents.length} saved` : "Browse"}
              </button>
            </div>

            {/* Attached Files Preview */}
            {attachedFiles.length > 0 && (
              <div className="mb-3">
                <div className="flex flex-wrap gap-2">
                  {attachedFiles.map((file, index) => (
                    <div
                      key={index}
                      className="flex items-center gap-2 bg-blue-50 text-blue-700 px-3 py-1 rounded-full text-sm"
                    >
                      <span>{file.name}</span>
                      <button
                        type="button"
                        onClick={() =>
                          setAttachedFiles((files) =>
                            files.filter((_, i) => i !== index)
                          )
                        }
                        className="text-blue-500 hover:text-blue-700"
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Message Input */}
            <div className="flex items-end gap-3">
              <div className="flex-1">
                <Field
                  as="textarea"
                  name="message"
                  placeholder="Type your message here..."
                  rows={1}
                  className="w-full resize-none border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                  onInput={(e: React.FormEvent<HTMLTextAreaElement>) => {
                    const target = e.target as HTMLTextAreaElement;
                    target.style.height = "auto";
                    target.style.height =
                      Math.min(target.scrollHeight, 120) + "px";
                  }}
                  onKeyDown={(e: React.KeyboardEvent<HTMLTextAreaElement>) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      if (isValid && values.message.trim() && !isLoading) {
                        const textarea = e.currentTarget as HTMLTextAreaElement;
                        textarea.form?.dispatchEvent(
                          new Event("submit", {
                            cancelable: true,
                            bubbles: true,
                          })
                        );
                      }
                    }
                  }}
                />
              </div>

              <button
                type="submit"
                disabled={!isValid || !values.message.trim() || isLoading}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white p-3 rounded-lg transition-colors duration-200 flex items-center justify-center"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </Form>
        )}
      </Formik>

      {/* File Attachment Modal */}
      <FileAttachmentModal
        isOpen={isFileModalOpen}
        onClose={() => setIsFileModalOpen(false)}
        onAttach={handleFileAttachment}
        currentFiles={attachedFiles}
      />

      {/* Documents Modal */}
      <DocumentsModal
        isOpen={isDocumentsModalOpen}
        onClose={() => setIsDocumentsModalOpen(false)}
      />
    </div>
  );
};

import type { ChatState, Conversation, Message } from "../types";

import type { DocumentItem } from "../services/documentsService";
import type { PayloadAction } from "@reduxjs/toolkit";
import { createSlice } from "@reduxjs/toolkit";

const initialState: ChatState = {
  conversations: [],
  activeConversationId: null,
  isLoading: false,
  documents: [],
  selectedModel: "gpt-3.5-turbo",
};

const chatSlice = createSlice({
  name: "chat",
  initialState,
  reducers: {
    setActiveConversation: (state, action: PayloadAction<string>) => {
      state.activeConversationId = action.payload;
    },
    createConversation: (state, action: PayloadAction<Conversation>) => {
      state.conversations.unshift(action.payload);
      state.activeConversationId = action.payload.id;
    },
    addMessage: (
      state,
      action: PayloadAction<{ conversationId: string; message: Message }>
    ) => {
      const conversation = state.conversations.find(
        (c) => c.id === action.payload.conversationId
      );
      if (conversation) {
        conversation.messages.push(action.payload.message);
        conversation.updatedAt = new Date();
      }
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setSelectedModel: (state, action: PayloadAction<string>) => {
      state.selectedModel = action.payload;
    },
    updateConversationTitle: (
      state,
      action: PayloadAction<{ id: string; title: string }>
    ) => {
      const conversation = state.conversations.find(
        (c) => c.id === action.payload.id
      );
      if (conversation) {
        conversation.title = action.payload.title;
      }
    },
    addDocuments: (state, action: PayloadAction<DocumentItem[]>) => {
      // Add documents that aren't already in the state
      action.payload.forEach((doc) => {
        if (
          !state.documents.find(
            (d) => d.checksum_sha256 === doc.checksum_sha256
          )
        ) {
          state.documents.push(doc);
        }
      });
    },
    removeDocuments: (state, action: PayloadAction<string[]>) => {
      // Remove documents by checksum
      state.documents = state.documents.filter(
        (doc) => !action.payload.includes(doc.checksum_sha256)
      );
    },
    setDocuments: (state, action: PayloadAction<DocumentItem[]>) => {
      state.documents = action.payload;
    },
  },
});

export const {
  setActiveConversation,
  createConversation,
  addMessage,
  setLoading,
  setSelectedModel,
  updateConversationTitle,
  addDocuments,
  removeDocuments,
  setDocuments,
} = chatSlice.actions;

export default chatSlice.reducer;

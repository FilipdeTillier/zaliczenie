import type { ChatState, Conversation, Message } from "../types";

import type { PayloadAction } from "@reduxjs/toolkit";
import { createSlice } from "@reduxjs/toolkit";

const initialState: ChatState = {
  conversations: [],
  activeConversationId: null,
  isLoading: false,
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
  },
});

export const {
  setActiveConversation,
  createConversation,
  addMessage,
  setLoading,
  updateConversationTitle,
} = chatSlice.actions;

export default chatSlice.reducer;

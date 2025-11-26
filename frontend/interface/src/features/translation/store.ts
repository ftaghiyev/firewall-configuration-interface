import { create } from "zustand";
import type { Context } from "./types";

interface TranslationStore {
  message: string;
  setMessage: (newMessage: string) => void;
  context: Context;
  setContextDescription: (newDescription: string) => void;
  setContextDetails: (newDetails: Record<string, any> | undefined) => void;
}

export const useTranslationStore = create<TranslationStore>((set) => ({
  message: "",
  setMessage: (newMessage: string) => set({ message: newMessage }),

  context: { description: "", details: undefined },
  setContextDescription: (newDescription: string) =>
    set((s) => ({ context: { ...s.context, description: newDescription } })),
  setContextDetails: (newDetails: Record<string, any> | undefined) =>
    set((s) => ({ context: { ...s.context, details: newDetails } })),
}));

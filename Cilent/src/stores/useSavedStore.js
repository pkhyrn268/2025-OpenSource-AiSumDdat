import { create } from "zustand";

export const useSavedStore = create((set) => ({
  savedList: [],
  addSaved: (item) => set((state) => ({ savedList: [...state.savedList, item] })),
  deleteSaved: (id) => set((state) => ({
    savedList: state.savedList.filter((it) => it.id !== id),
  })),
  clearSaved: () => set({ savedList: [] }),
}));

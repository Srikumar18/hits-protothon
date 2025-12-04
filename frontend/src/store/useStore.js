import { create } from 'zustand';
import { mockData } from '../data/mockData';

export const useStore = create((set) => ({
    activeTab: 'summary', // summary, hierarchy, json, tables
    setActiveTab: (tab) => set({ activeTab: tab }),

    files: [],
    currentFile: null,

    // allow updating currentFile (used to store backend extraction result)
    setCurrentFile: (data) => set({ currentFile: data }),

    sidebarOpen: true,
    toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),

    currentPage: 1,
    setCurrentPage: (page) => set({ currentPage: page }),

    selectedNodeId: null,
    setSelectedNodeId: (id) => set({ selectedNodeId: id }),

    // Mock actions
    uploadFile: (file) => {
        console.log('Uploading file:', file);
        set((state) => ({
            files: [
                {
                    id: Math.random().toString(36).substr(2, 9),
                    name: file.name,
                    date: new Date().toISOString().split('T')[0]
                },
                ...state.files
            ]
        }));
    },
}));

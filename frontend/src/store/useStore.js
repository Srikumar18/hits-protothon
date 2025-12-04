import { create } from 'zustand';
import { mockData } from '../data/mockData';

export const useStore = create((set) => ({
    activeTab: 'summary', // summary, hierarchy, json, tables
    setActiveTab: (tab) => set({ activeTab: tab }),

    files: [
        { id: '1', name: 'Assignment-1-1135.pdf', date: '2025-12-04' },
        { id: '2', name: 'Research_Paper_v2.pdf', date: '2025-12-03' },
        { id: '3', name: 'Invoice_Dec_2025.pdf', date: '2025-12-01' },
    ],
    currentFile: mockData,

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

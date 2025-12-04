import { create } from 'zustand';

export const useStore = create((set, get) => ({
    activeTab: 'summary',
    setActiveTab: (tab) => set({ activeTab: tab }),

    // Uploaded files list
    files: [],

    // All extracted file results in the session
    sessions: [],   // ← NEW

    // The file currently being viewed
    currentFile: null,

    // Save extracted data and update currentFile
    addSession: (fileId, data) =>
        set((state) => ({
            sessions: [
                ...state.sessions,
                { fileId, data }, // store entire extracted result
            ],
            currentFile: data, // automatically switch view
        })),

    // Called when user clicks a file in sidebar
    loadSession: (fileId) => {
        const session = get().sessions.find((s) => s.fileId === fileId);
        if (session) {
            set({ currentFile: session.data });
        }
    },

    setCurrentFile: (data) => set({ currentFile: data }),

    sidebarOpen: true,
    toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),

    currentPage: 1,
    setCurrentPage: (page) => set({ currentPage: page }),

    selectedNodeId: null,
    setSelectedNodeId: (id) => set({ selectedNodeId: id }),

    // Handle uploaded file metadata
    uploadFile: (file) => {
        const id = Math.random().toString(36).substr(2, 9);

        set((state) => ({
            files: [
                {
                    id,
                    name: file.name,
                    date: new Date().toISOString().split('T')[0]
                },
                ...state.files
            ]
        }));

        return id; // return fileId so backend response can link it
    },
}));

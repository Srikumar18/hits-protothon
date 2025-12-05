import { create } from 'zustand';

export const useStore = create((set, get) => ({

    /* ------------------------------------
       UI TABS
    ------------------------------------ */
    activeTab: 'summary',
    setActiveTab: (tab) => set({ activeTab: tab }),


    /* ------------------------------------
       GLOBAL LOADING STATE (for upload)
    ------------------------------------ */
    isLoading: false,
    setLoading: (status) => set({ isLoading: status }),


    /* ------------------------------------
       FILE LIST (names only)
    ------------------------------------ */
    files: [],

    uploadFile: (file) => {
        const id = Math.random().toString(36).substring(2, 9);

        set((state) => ({
            files: [
                {
                    id,
                    name: file.name,
                    date: new Date().toISOString().split("T")[0],
                },
                ...state.files,
            ],
        }));

        return id;
    },


    /* ------------------------------------
       SESSION STORAGE (full extraction data)
    ------------------------------------ */
    sessions: [],
    currentFile: null,

    addSession: (fileId, data) =>
        set((state) => ({
            sessions: [...state.sessions, { fileId, data }],
            currentFile: data,
            currentPage: 1,
        })),

    loadSession: (fileId) => {
        const session = get().sessions.find((s) => s.fileId === fileId);
        if (session) {
            set({
                currentFile: session.data,
                currentPage: 1,
            });
        }
    },

    setCurrentFile: (data) =>
        set({
            currentFile: data,
            currentPage: 1,
        }),


    /* ------------------------------------
       SIDEBAR
    ------------------------------------ */
    sidebarOpen: true,
    toggleSidebar: () =>
        set((state) => ({ sidebarOpen: !state.sidebarOpen })),


    /* ------------------------------------
       PDF VIEWER STATE
    ------------------------------------ */
    currentPage: 1,
    setCurrentPage: (page) => set({ currentPage: page }),

    selectedNodeId: null,
    setSelectedNodeId: (id) => set({ selectedNodeId: id }),


    /* ------------------------------------
       PDF MODAL VIEWER STATE
    ------------------------------------ */
    pdfViewerOpen: false,
    pdfViewerUrl: null,
    pdfViewerTitle: null,
    pdfViewerPage: 1,

    openPDFViewer: (url, title, page = 1) =>
        set({
            pdfViewerOpen: true,
            pdfViewerUrl: url,
            pdfViewerTitle: title,
            pdfViewerPage: page,
        }),

    closePDFViewer: () =>
        set({
            pdfViewerOpen: false,
            pdfViewerUrl: null,
            pdfViewerTitle: null,
            pdfViewerPage: 1,
        }),

}));

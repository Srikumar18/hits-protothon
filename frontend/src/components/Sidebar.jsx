import React from 'react';
import { useStore } from '../store/useStore';
import {
    Upload,
    FileText,
    Eye,
    ChevronDown,
    ChevronRight
} from 'lucide-react';
import { motion } from 'framer-motion';
import clsx from 'clsx';
import axiosInstance from '../utils/axiosInstance';

const Sidebar = () => {
    const {
        sidebarOpen,
        files,
        uploadFile,
        setCurrentFile,
        addSession,
        loadSession,
        sessions,
        openPDFViewer,
        currentFile
    } = useStore();

    const [isSavedOpen, setIsSavedOpen] = React.useState(true);
    const fileInputRef = React.useRef(null);

    const handleUploadClick = () => {
        fileInputRef.current?.click();
    };

    const { setLoading } = useStore();

    const handleFileChange = async (event) => {
        const file = event.target.files?.[0];
        if (!file) return;

        const fileId = uploadFile(file);

        try {
            setLoading(true);  

            const formData = new FormData();
            formData.append('file', file);

            const response = await axiosInstance.post(
                '/extract-pdf',
                formData,
                { headers: { 'Content-Type': 'multipart/form-data' } }
            );

            addSession(fileId, response.data);
            setCurrentFile(response.data);

        } catch (err) {
            console.error("Error sending file:", err);
        } finally {
            setLoading(false); 
        }
    };


    if (!sidebarOpen) return null;

    return (
        <motion.div
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 280, opacity: 1 }}
            className="h-screen bg-secondary/30 border-r border-border flex flex-col"
        >
            {/* Header */}
            <div className="p-4 border-b border-border">
                <div className="flex items-center gap-2 mb-6">
                    <div className="w-8 h-8 bg-gradient-to-r from-black to-gray-800 rounded-lg flex items-center justify-center text-white font-bold">
                        D
                    </div>
                    <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-black to-gray-800 text-transparent bg-clip-text">DocMind</span>
                </div>

                <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleFileChange}
                    className="hidden"
                    accept=".pdf"
                />

                <button
                    onClick={handleUploadClick}
                    className="w-full bg-primary text-primary-foreground hover:bg-primary/90 h-10 rounded-md 
                               flex items-center justify-center gap-2 text-sm font-medium transition-colors shadow-sm"
                >
                    <Upload size={16} />
                    Upload PDF
                </button>
            </div>

            {/* Session Files */}
            <div className="flex-1 overflow-y-auto p-2">
                <button
                    onClick={() => setIsSavedOpen(!isSavedOpen)}
                    className="w-full flex items-center gap-1 p-2 text-xs font-semibold 
                               text-muted-foreground hover:text-foreground transition-colors"
                >
                    {isSavedOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                    SESSION FILES
                </button>

                {isSavedOpen && (
                    <div className="space-y-1 mt-1">
                        {files.length === 0 ? (
                            <p className="text-xs text-muted-foreground px-2 py-1">No files uploaded</p>
                        ) : (
                            files.map((file) => {
                                const session = sessions.find(s => s.fileId === file.id);
                                const isActive = currentFile && session?.data?.pdf_url === currentFile?.pdf_url;

                                return (
                                    <div
                                        key={file.id}
                                        className={clsx(
                                            "group flex items-center gap-2 p-2 rounded-md text-sm transition-colors cursor-pointer",
                                            isActive
                                                ? "bg-blue-500 text-white border border-blue-600 shadow-sm"
                                                : "text-muted-foreground hover:text-foreground hover:bg-accent/50"
                                        )}
                                        onClick={() => loadSession(file.id)}
                                    >
                                        <FileText size={16} />

                                        <span className="truncate flex-1">
                                            {file.name}
                                        </span>

                                        {/* View Button */}
                                        <button
                                            className={clsx(
                                                "p-1 rounded transition-opacity",
                                                isActive
                                                    ? "text-white hover:bg-blue-600"
                                                    : "opacity-0 group-hover:opacity-100 hover:bg-background"
                                            )}
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                if (session?.data?.pdf_url) {
                                                    openPDFViewer(session.data.pdf_url, file.name, 1);
                                                }
                                            }}
                                            title="View PDF"
                                        >
                                            <Eye size={14} />
                                        </button>
                                    </div>
                                );
                            })
                        )}
                    </div>
                )}
            </div>
        </motion.div>
    );
};

export default Sidebar;

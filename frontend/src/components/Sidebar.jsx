import React from 'react';
import { useStore } from '../store/useStore';
import {
    Upload,
    FileText,
    Folder,
    MoreVertical,
    ChevronRight,
    ChevronDown,
    Plus
} from 'lucide-react';
import { motion } from 'framer-motion';
import clsx from 'clsx';
import axios from 'axios';

const Sidebar = () => {
    const { sidebarOpen, files, uploadFile, setCurrentFile } = useStore();
    const [isSavedOpen, setIsSavedOpen] = React.useState(true);
    const fileInputRef = React.useRef(null);

    const handleUploadClick = () => {
        fileInputRef.current?.click();
    };

    const handleFileChange = async (event) => {
        const file = event.target.files?.[0];
        if (!file) return;

        // keep existing local behavior
        uploadFile(file);

        // send file to backend for extraction
        try {
            const formData = new FormData();
            formData.append('file', file);

            // Pass formData as the request body and optional headers as config
            const response = await axios.post(
                'http://localhost:8000/extract-pdf',
                formData,
                {
                    headers: { 'Content-Type': 'multipart/form-data' },
                }
            );

            if (response.status < 200 || response.status >= 300) {
                console.error('Extraction request failed:', response.statusText || response.status);
                return;
            }

            console.log('Extraction response:', response.data);

            // update global state so JSONViewer displays backend result
            setCurrentFile(response.data);
        } catch (err) {
            console.error('Error sending file to extract-pdf:', err);
        }
    };

    if (!sidebarOpen) return null;

    return (
        <motion.div
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 280, opacity: 1 }}
            className="h-screen bg-secondary/30 border-r border-border flex flex-col"
        >
            <div className="p-4 border-b border-border">
                <div className="flex items-center gap-2 mb-6">
                    <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center text-primary-foreground font-bold">
                        D
                    </div>
                    <span className="font-bold text-lg tracking-tight">DocMind</span>
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
                    className="w-full bg-primary text-primary-foreground hover:bg-primary/90 h-10 rounded-md flex items-center justify-center gap-2 text-sm font-medium transition-colors shadow-sm"
                >
                    <Upload size={16} />
                    Upload PDF
                </button>
            </div>

            <div className="flex-1 overflow-y-auto p-2">
                <div className="mb-2">
                    <button
                        onClick={() => setIsSavedOpen(!isSavedOpen)}
                        className="w-full flex items-center gap-1 p-2 text-xs font-semibold text-muted-foreground hover:text-foreground transition-colors"
                    >
                        {isSavedOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                        SAVED FILES
                    </button>

                    {isSavedOpen && (
                        <div className="space-y-1 mt-1">
                            {files.map((file) => (
                                <div
                                    key={file.id}
                                    className={clsx(
                                        "group flex items-center gap-2 p-2 rounded-md text-sm cursor-pointer transition-colors",
                                        file.id === '1' ? "bg-accent text-accent-foreground" : "hover:bg-accent/50 text-muted-foreground hover:text-foreground"
                                    )}
                                >
                                    <FileText size={16} />
                                    <span className="truncate flex-1">{file.name}</span>
                                    <button className="opacity-0 group-hover:opacity-100 p-1 hover:bg-background rounded">
                                        <MoreVertical size={14} />
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                <div className="mt-4">
                    <button
                        className="w-full flex items-center gap-1 p-2 text-xs font-semibold text-muted-foreground hover:text-foreground transition-colors"
                    >
                        <ChevronRight size={14} />
                        FOLDERS
                    </button>
                </div>
            </div>

            
        </motion.div>
    );
};

export default Sidebar;

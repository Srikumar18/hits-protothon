import React from 'react';
import { FileJson } from 'lucide-react';
import { useStore } from '../store/useStore';
import LoadingScreen from './LoadingScreen';

const Toolbar = () => {
    const { currentFile, isLoading } = useStore();

    const handleExportJSON = () => {
        if (!currentFile) return;
        const jsonString = JSON.stringify(currentFile, null, 2);
        const blob = new Blob([jsonString], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'document_data.json';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    };

    const ActionButton = ({ icon: Icon, label, primary = false, onClick }) => (
        <button
            onClick={onClick}
            className={`
                flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium transition-all
                ${primary
                    ? 'bg-primary text-primary-foreground hover:bg-primary/90 shadow-sm'
                    : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                }
            `}
        >
            <Icon size={16} />
            {label}
        </button>
    );

    /* -----------------------------------------
       1️⃣ Show loading screen when uploading
    ------------------------------------------ */
    if (isLoading) {
        return <LoadingScreen />;
    }

    /* -----------------------------------------
       2️⃣ Show welcome logo if no file loaded
    ------------------------------------------ */
    if (!currentFile) {
        return (
            <div className="relative flex flex-col items-center justify-center h-full w-full select-none gap-4 overflow-hidden">

                {/* 🔥 Bottom Vignette Gradient (covers only bottom 60%) */}
                <div className="
                    pointer-events-none 
                    absolute bottom-0 left-0 right-0 h-[60%]
                    bg-gradient-to-t from-black/60 via-gray-900/30 to-transparent
                " />

                {/* Logo Box */}
                <div className="bg-gradient-to-r from-black to-gray-800 
                                rounded-xl px-12 py-6 shadow-lg relative z-10">
                    <h1 className="text-5xl font-extrabold text-white tracking-tight">
                        JsonifyPDF
                    </h1>
                </div>

                {/* Tagline */}
                <p className="mt-2 text-base text-muted-foreground relative z-10">
                    Extract. Understand. Visualize your documents effortlessly.
                </p>

                {/* Bottom Prompt (always pinned) */}
                <p className="absolute bottom-10 text-sm font-semibold text-white z-10">
                    Upload a PDF to get started
                </p>

            </div>
        );
    }



    /* -----------------------------------------
       3️⃣ Normal toolbar (PDF loaded)
    ------------------------------------------ */
    return (
        <div className="h-14 border-b border-border bg-background/95 backdrop-blur 
                        supports-[backdrop-filter]:bg-background/60 flex items-center 
                        justify-between px-4 sticky top-0 z-10">

            <div className="flex items-center gap-2"></div>

            <div className="flex items-center gap-2">
                <div className="h-4 w-px bg-border mx-2" />
                <ActionButton 
                    icon={FileJson} 
                    label="Export JSON" 
                    onClick={handleExportJSON} 
                    primary 
                />
            </div>
        </div>
    );
};

export default Toolbar;

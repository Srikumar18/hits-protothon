import React from 'react';
import {
    Layout,
    FileJson,
    FileText,
    Download,
    Sparkles
} from 'lucide-react';

import { useStore } from '../store/useStore';

const Toolbar = () => {
    const { currentFile } = useStore();

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

    return (
        <div className="h-14 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 flex items-center justify-between px-4 sticky top-0 z-10">
            <div className="flex items-center gap-2">
                {/* Action buttons removed as per request */}
            </div>

            <div className="flex items-center gap-2">
                <div className="h-4 w-px bg-border mx-2" />
                <ActionButton icon={FileJson} label="Export JSON" onClick={handleExportJSON} primary />
            </div>
        </div>
    );
};

export default Toolbar;

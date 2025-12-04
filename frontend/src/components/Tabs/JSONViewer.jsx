import React from 'react';
import ReactJson from 'react-json-view';
import { useStore } from '../../store/useStore';
import { Copy, Check } from 'lucide-react';

const JSONViewer = () => {
    const { currentFile } = useStore();
    const [copied, setCopied] = React.useState(false);

    const handleCopy = () => {
        if (!currentFile) return;
        navigator.clipboard.writeText(JSON.stringify(currentFile, null, 2));
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="h-full overflow-y-auto p-4 bg-background relative group">
            <button
                onClick={handleCopy}
                className="absolute top-4 right-4 p-2 rounded-md bg-secondary/50 hover:bg-secondary text-muted-foreground hover:text-foreground transition-all opacity-0 group-hover:opacity-100 z-10"
                title="Copy JSON"
            >
                {copied ? <Check size={16} className="text-green-500" /> : <Copy size={16} />}
            </button>
            <ReactJson
                src={currentFile || {}}
                theme="rjv-default"
                displayDataTypes={false}
                enableClipboard={false}
                style={{ backgroundColor: 'transparent', fontSize: '13px' }}
            />
        </div>
    );
};

export default JSONViewer;

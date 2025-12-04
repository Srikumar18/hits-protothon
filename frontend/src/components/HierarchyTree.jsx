import React, { useState } from 'react';
import { ChevronRight, ChevronDown, Hash, Type, Image as ImageIcon, Table } from 'lucide-react';
import clsx from 'clsx';
import { useStore } from '../store/useStore';

const NodeIcon = ({ type }) => {
    switch (type) {
        case 'heading': return <Hash size={14} className="text-blue-500" />;
        case 'paragraph': return <Type size={14} className="text-gray-500" />;
        case 'image': return <ImageIcon size={14} className="text-purple-500" />;
        case 'table': return <Table size={14} className="text-green-500" />;
        default: return <Type size={14} className="text-gray-400" />;
    }
};

const TreeNode = ({ node, level = 0 }) => {
    const [isOpen, setIsOpen] = useState(true);
    
    const { 
        selectedNodeId, 
        setSelectedNodeId, 
        setCurrentPage, 
        openPDFViewer, 
        currentFile 
    } = useStore();

    const hasChildren = node.children?.length > 0;

    const handleToggle = (e) => {
        e.stopPropagation();
        setIsOpen(!isOpen);
    };

    const handleSelect = () => {
        setSelectedNodeId(node.id);

        if (node.page_refs?.length > 0) {
            const page = node.page_refs[0].page;

            console.log("📄 Hierarchy clicked → Page:", page);

            // Update left-side PDF viewer page
            setCurrentPage(page);

            // Open modal viewer starting at this page
            if (currentFile?.pdf_url) {
                openPDFViewer(currentFile.pdf_url, currentFile.name, page);
            }
        }
    };

    return (
        <div className="select-none">
            <div
                className={clsx(
                    "flex items-center gap-2 py-1.5 px-2 rounded-md cursor-pointer transition-colors text-sm",
                    selectedNodeId === node.id
                        ? "bg-primary/10 text-primary"
                        : "hover:bg-accent text-muted-foreground hover:text-foreground"
                )}
                style={{ paddingLeft: `${level * 12 + 8}px` }}
                onClick={handleSelect}
            >
                <div
                    onClick={hasChildren ? handleToggle : undefined}
                    className={clsx(
                        "p-0.5 rounded hover:bg-black/5 transition-colors",
                        !hasChildren && "opacity-0"
                    )}
                >
                    {isOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                </div>

                <NodeIcon type={node.type} />
                <span className="truncate flex-1">{node.text || node.type}</span>

                {node.page_refs?.[0] && (
                    <span className="text-[10px] text-muted-foreground bg-accent px-1.5 py-0.5 rounded">
                        p.{node.page_refs[0].page}
                    </span>
                )}
            </div>

            {hasChildren && isOpen && (
                <div>
                    {node.children.map((child) => (
                        <TreeNode key={child.id} node={child} level={level + 1} />
                    ))}
                </div>
            )}
        </div>
    );
};

const HierarchyTree = () => {
    const { currentFile } = useStore();

    if (!currentFile?.structure) return null;

    return (
        <div className="h-full overflow-y-auto p-2">
            <TreeNode node={currentFile.structure} />
        </div>
    );
};

export default HierarchyTree;

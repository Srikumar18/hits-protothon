import React from 'react';
import { useStore } from '../store/useStore';
import { X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const PDFViewerModal = () => {
    const {
        pdfViewerOpen,
        pdfViewerUrl,
        pdfViewerTitle,
        pdfViewerPage,   // ← NEW
        closePDFViewer
    } = useStore();

    const handleBackdropClick = (e) => {
        if (e.target === e.currentTarget) {
            closePDFViewer();
        }
    };

    // Build the viewer URL with page parameter
    const viewerSrc = pdfViewerUrl
    ? `http://localhost:8000${pdfViewerUrl}#page=${pdfViewerPage}`
    : null;


    return (
        <AnimatePresence>
            {pdfViewerOpen && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
                    onClick={handleBackdropClick}
                >
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        exit={{ scale: 0.9, opacity: 0 }}
                        className="bg-white rounded-lg shadow-2xl w-full max-w-4xl h-[90vh] flex flex-col"
                        onClick={(e) => e.stopPropagation()}
                    >
                        {/* Header */}
                        <div className="flex items-center justify-between p-4 border-b border-gray-200">
                            <h2 className="text-lg font-semibold text-gray-900 truncate">
                                {pdfViewerTitle || 'PDF Viewer'}
                            </h2>
                            <button
                                onClick={closePDFViewer}
                                className="p-2 hover:bg-gray-100 rounded-full transition-colors"
                                title="Close"
                            >
                                <X size={20} />
                            </button>
                        </div>

                        {/* PDF Content */}
                        <div className="flex-1 overflow-hidden">
                            {viewerSrc && (
                                <iframe
                                    src={viewerSrc}
                                    className="w-full h-full border-0"
                                    title={pdfViewerTitle || 'PDF Document'}
                                />
                            )}
                        </div>
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    );
};

export default PDFViewerModal;

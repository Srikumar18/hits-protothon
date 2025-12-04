import React, { useState } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import { useStore } from '../store/useStore';
import { ChevronLeft, ChevronRight, ZoomIn, ZoomOut, FileText } from 'lucide-react';
import 'react-pdf/dist/esm/Page/AnnotationLayer.css';
import 'react-pdf/dist/esm/Page/TextLayer.css';

// Configure PDF worker
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

const PDFViewer = () => {
    const { currentFile, currentPage, setCurrentPage } = useStore();
    const [numPages, setNumPages] = useState(null);
    const [scale, setScale] = useState(1.0);
    const [showOverlay, setShowOverlay] = useState(false); // Default to false to avoid confusion

    function onDocumentLoadSuccess({ numPages }) {
        setNumPages(numPages);
    }

    // Get text blocks for current page
    const currentPageData = currentFile?.pages?.find(p => p.page === currentPage);
    const textBlocks = currentPageData?.text_blocks || [];

    return (
        <div className="h-full flex flex-col bg-slate-50">
            {/* Toolbar */}
            <div className="h-14 bg-white border-b border-border flex items-center justify-between px-6 shadow-sm z-10">
                <div className="flex items-center gap-3">
                    <div className="flex items-center bg-secondary/50 rounded-lg p-1">
                        <button
                            onClick={() => setCurrentPage(Math.max(currentPage - 1, 1))}
                            disabled={currentPage <= 1}
                            className="p-1.5 hover:bg-white rounded-md disabled:opacity-50 transition-all shadow-sm disabled:shadow-none"
                        >
                            <ChevronLeft size={16} />
                        </button>
                        <span className="text-sm font-medium px-3 min-w-[80px] text-center">
                            {numPages ? `${currentPage} / ${numPages}` : '--'}
                        </span>
                        <button
                            onClick={() => setCurrentPage(Math.min(currentPage + 1, numPages || 1))}
                            disabled={currentPage >= numPages}
                            className="p-1.5 hover:bg-white rounded-md disabled:opacity-50 transition-all shadow-sm disabled:shadow-none"
                        >
                            <ChevronRight size={16} />
                        </button>
                    </div>
                    <div className="h-6 w-px bg-border mx-2" />
                    <label className="flex items-center gap-2 text-sm font-medium cursor-pointer select-none text-muted-foreground hover:text-foreground transition-colors">
                        <input
                            type="checkbox"
                            checked={showOverlay}
                            onChange={(e) => setShowOverlay(e.target.checked)}
                            className="rounded border-gray-300 text-primary focus:ring-primary"
                        />
                        Show OCR Overlay
                    </label>
                </div>

                <div className="flex items-center gap-2 bg-secondary/50 rounded-lg p-1">
                    <button
                        onClick={() => setScale(s => Math.max(s - 0.1, 0.5))}
                        className="p-1.5 hover:bg-white rounded-md transition-all shadow-sm"
                    >
                        <ZoomOut size={16} />
                    </button>
                    <span className="text-sm font-medium w-12 text-center">
                        {(scale * 100).toFixed(0)}%
                    </span>
                    <button
                        onClick={() => setScale(s => Math.min(s + 0.1, 2.0))}
                        className="p-1.5 hover:bg-white rounded-md transition-all shadow-sm"
                    >
                        <ZoomIn size={16} />
                    </button>
                </div>
            </div>

            {/* PDF Content */}
            <div className="flex-1 overflow-auto flex justify-center p-8 bg-slate-50/50">
                {!currentFile?.pdf_url ? (
                    <div className="flex items-center justify-center h-full">
                        <div className="text-center text-muted-foreground">
                            <FileText size={48} className="mx-auto mb-4 opacity-50" />
                            <p className="text-lg font-medium">No PDF loaded</p>
                            <p className="text-sm">Upload a PDF to view it here</p>
                        </div>
                    </div>
                ) : (
                <div className="relative shadow-2xl transition-all duration-300 ease-in-out" style={{ transform: `scale(${scale})`, transformOrigin: 'top center' }}>
                    <Document
                        file={currentFile?.pdf_url ? `http://localhost:8000${currentFile.pdf_url}` : null}
                        onLoadSuccess={onDocumentLoadSuccess}
                        className="flex flex-col gap-4"
                        loading={
                            <div className="h-[800px] w-[600px] bg-white flex items-center justify-center rounded-lg shadow-sm border border-border">
                                <div className="flex flex-col items-center gap-2 text-muted-foreground">
                                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                                    <span className="text-sm font-medium">Loading Document...</span>
                                </div>
                            </div>
                        }
                        error={
                            <div className="h-[800px] w-[600px] bg-white flex items-center justify-center text-destructive rounded-lg shadow-sm border border-border">
                                <span className="text-sm font-medium">Failed to load PDF</span>
                            </div>
                        }
                    >
                        <Page
                            pageNumber={currentPage}
                            scale={1} // Handle scale via CSS transform for smoother zoom
                            renderTextLayer={true}
                            renderAnnotationLayer={true}
                            className="bg-white"
                        />

                        {/* Overlay Layer for Bounding Boxes */}
                        {showOverlay && (
                            <div className="absolute inset-0 pointer-events-none">
                                {textBlocks.map((block) => (
                                    <div
                                        key={block.block_id}
                                        className="absolute border border-blue-500/50 bg-blue-500/10 hover:bg-blue-500/20 transition-colors cursor-pointer z-10"
                                        style={{
                                            left: `${block.bbox[0]}px`,
                                            top: `${block.bbox[1]}px`,
                                            width: `${block.bbox[2]}px`,
                                            height: `${block.bbox[3]}px`,
                                        }}
                                        title={`${block.type}: ${block.text}`}
                                    />
                                ))}
                            </div>
                        )}
                    </Document>
                </div>
                )}
            </div>
        </div>
    );
};

export default PDFViewer;

import React from 'react';
import { useStore } from '../../store/useStore';
import { Tag, Sparkles } from 'lucide-react';

const SummaryKeywords = () => {
    const { currentFile } = useStore();
    const summary = currentFile?.summary;
    const metadata = currentFile?.metadata;

    // If no data yet, render nothing
    if (!summary || !metadata) return null;

    return (
        <div className="h-full overflow-y-auto p-6 bg-background space-y-8">
            {/* Summary Section */}
            {summary?.auto_summary && (
                <div className="space-y-3">
                    <div className="flex items-center gap-2 text-primary font-semibold">
                        <Sparkles size={18} />
                        <h3>Executive Summary</h3>
                    </div>
                    <div className="p-4 bg-primary/5 rounded-lg border border-primary/10 text-sm leading-relaxed text-foreground/90">
                        {summary.auto_summary}
                    </div>
                </div>
            )}

            {/* Keywords Section */}
            {summary?.keywords?.length > 0 && (
                <div className="space-y-3">
                    <div className="flex items-center gap-2 text-primary font-semibold">
                        <Tag size={18} />
                        <h3>Keywords</h3>
                    </div>
                    <div className="flex flex-wrap gap-2">
                        {summary.keywords.map((keyword, index) => (
                            <span
                                key={index}
                                className="px-3 py-1 bg-accent hover:bg-accent/80 text-accent-foreground text-sm rounded-full cursor-pointer transition-colors border border-transparent hover:border-border"
                            >
                                #{keyword}
                            </span>
                        ))}
                    </div>
                </div>
            )}

            {/* Metadata Section */}
            <div className="pt-6 border-t border-border">
                <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-4">
                    Metadata
                </h3>

                <div className="grid grid-cols-2 gap-4 text-sm">
                    
                    {metadata?.ocr_engine && (
                        <div>
                            <span className="text-muted-foreground block text-xs">OCR Engine</span>
                            <span className="font-medium">
                                {metadata.ocr_engine} {metadata?.ocr_version || ""}
                            </span>
                        </div>
                    )}

                    {typeof metadata?.avg_ocr_confidence === "number" && (
                        <div>
                            <span className="text-muted-foreground block text-xs">Confidence</span>
                            <span className="font-medium">
                                {(metadata.avg_ocr_confidence * 100).toFixed(1)}%
                            </span>
                        </div>
                    )}

                    {metadata?.generated_at && (
                        <div>
                            <span className="text-muted-foreground block text-xs">Generated At</span>
                            <span className="font-medium">
                                {new Date(metadata.generated_at).toLocaleDateString()}
                            </span>
                        </div>
                    )}

                    {Array.isArray(metadata?.pipeline) && metadata.pipeline.length > 0 && (
                        <div>
                            <span className="text-muted-foreground block text-xs">Pipeline</span>
                            <span
                                className="font-medium text-xs truncate block"
                                title={metadata.pipeline.join(', ')}
                            >
                                {metadata.pipeline.length} steps
                            </span>
                        </div>
                    )}
                    
                </div>
            </div>
        </div>
    );
};

export default SummaryKeywords;

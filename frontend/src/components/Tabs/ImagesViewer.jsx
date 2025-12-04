import React, { useState } from 'react';
import { useStore } from '../../store/useStore';
import { Image as ImageIcon } from 'lucide-react';
import ImageTile from '../ImageTile';

const ImagesViewer = () => {
    const { currentFile } = useStore();
    const [selectedImage, setSelectedImage] = useState(null);

    // Flatten images from all pages
    const images =
        currentFile?.pages?.flatMap((p) =>
            p.images.map((img) => ({ src: img, page: p.page }))
        ) || [];

    if (images.length === 0) {
        return (
            <div className="h-full flex flex-col items-center justify-center text-muted-foreground gap-2">
                <ImageIcon size={48} className="opacity-20" />
                <p>No images found in this document.</p>
            </div>
        );
    }

    return (
        <div className="relative h-full overflow-y-auto p-6 bg-background">
            {/* Grid of images */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {images.map((img, index) => (
                    <div
                        key={index}
                        className="group relative aspect-square bg-muted/30 rounded-lg border border-border overflow-hidden hover:shadow-md transition-all cursor-pointer"
                        onClick={() =>
                            setSelectedImage(`http://localhost:8000${img.src}`)
                        }
                    >
                        <img
                            src={`http://localhost:8000${img.src}`}
                            alt="Extracted"
                            className="absolute inset-0 w-full h-full object-cover"
                        />
                        <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors" />
                    </div>
                ))}
            </div>

            {/* Modal for selected image */}
            {selectedImage && (
                <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
                    <ImageTile
                        src={selectedImage}
                        onClose={() => setSelectedImage(null)}
                    />
                </div>
            )}
        </div>
    );
};

export default ImagesViewer;

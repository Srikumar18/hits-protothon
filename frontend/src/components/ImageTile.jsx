import React from "react";
import { X } from "lucide-react";

const ImageTile = ({ src, onClose }) => {
    return (
        <div className="relative w-[500px] h-[500px] rounded-md overflow-hidden shadow-lg border bg-muted flex items-center justify-center">
            
            {/* Image fully visible with preserved aspect ratio */}
            <img
                src={src}
                alt="Extracted"
                className="max-w-full max-h-full object-contain"
            />

            {/* Close button */}
            <button
                onClick={onClose}
                className="
                    absolute top-2 right-2
                    w-8 h-8
                    flex items-center justify-center
                    rounded-full
                    bg-black/70 hover:bg-black/85
                    text-white 
                    transition
                "
            >
                <X size={18} />
            </button>
        </div>
    );
};

export default ImageTile;

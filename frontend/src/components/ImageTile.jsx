import React from "react";
import { X } from "lucide-react";

const ImageTile = ({ src, onClose }) => {
    return (
        <div className="relative w-[500px] h-[500px] rounded-md overflow-hidden shadow-sm border bg-muted">
            {/* Image */}
            <img
                src={src}
                alt="Extracted"
                className="w-full h-full object-cover"
            />

            {/* Close button */}
            <button
                onClick={onClose}
                className="
                    absolute top-1 right-1
                    w-6 h-6
                    flex items-center justify-center
                    rounded-full
                    bg-black/70 hover:bg-black/85 
                    text-white 
                    transition
                "
            >
                <X size={14} />
            </button>
        </div>
    );
};

export default ImageTile;

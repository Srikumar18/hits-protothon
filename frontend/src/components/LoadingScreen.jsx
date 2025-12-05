import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";

const LoadingScreen = () => {
    const [elapsed, setElapsed] = useState(0);

    useEffect(() => {
        const interval = setInterval(() => setElapsed((t) => t + 1), 1000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="h-screen w-full flex flex-col items-center justify-center bg-white relative">

            {/* Text */}
            <div className="text-center select-none px-4 py-2 rounded-xl">
                <h1 className="text-5xl font-extrabold bg-gradient-to-r from-blue-600 to-indigo-700 text-transparent bg-clip-text leading-tight">
                    Hang On Tight
                </h1>
                <p className="mt-3 text-lg text-gray-600">
                    Just a little time to upload the PDF...
                </p>
            </div>

            {/* Animated Bar */}
            <div className="relative w-[60%] mt-10 h-3 rounded-full overflow-hidden">
                <motion.div
                    className="absolute top-0 h-full bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full"
                    animate={{
                        // WIDTH changes (grow & shrink)
                        width: ["0%", "100%", "0%", "100%", "0%"],

                        // LEFT position shifts for right→left animation
                        left: ["0%", "0%", "100%", "0%", "100%"],

                        // RIGHT position shifts for left→right animation
                        right: ["100%", "0%", "0%", "100%", "0%"],
                    }}
                    transition={{
                        duration: 2.5,
                        repeat: Infinity,
                        ease: "easeInOut",
                    }}
                />
            </div>

            {/* Timer */}
            <div className="absolute bottom-4 left-4 text-sm text-gray-500 select-none">
                Elapsed: {elapsed}s
            </div>
        </div>
    );
};

export default LoadingScreen;

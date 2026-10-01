import React, { useEffect, useState } from 'react';
import { Loader2 } from 'lucide-react';

const STAGES = [
    "Looking closely at your artwork...",
    "Discovering visual details & palette...",
    "Consulting Context & Research Agents...",
    "Composing your immersive story chapters...",
    "Preparing interactive museum stage..."
];

export default function LoadingOverlay() {
    const [index, setIndex] = useState(0);

    useEffect(() => {
        const timer = setInterval(() => {
            setIndex((prev) => (prev < STAGES.length - 1 ? prev + 1 : prev));
        }, 1800);
        return () => clearInterval(timer);
    }, []);

    return (
        <div className="min-h-[500px] flex flex-col items-center justify-center p-8 space-y-6 text-center animate-fade-in">
            <div className="relative">
                <div className="w-16 h-16 rounded-full border-4 border-stone-200 dark:border-stone-800 border-t-amber-600 animate-spin" />
                <Loader2 className="w-6 h-6 text-amber-600 absolute inset-0 m-auto animate-pulse" />
            </div>
            <div className="space-y-2">
                <h3 className="font-serif text-2xl text-stone-900 dark:text-stone-100">KalaKatha Orchestrator</h3>
                <p className="text-sm font-sans text-stone-600 dark:text-stone-400 tracking-wide transition-all duration-300">
                    {STAGES[index]}
                </p>
            </div>
            <div className="flex gap-1.5 pt-2">
                {STAGES.map((_, i) => (
                    <div
                        key={i}
                        className={`h-1 rounded-full transition-all duration-500 ${i <= index ? 'w-6 bg-amber-600' : 'w-2 bg-stone-300 dark:bg-stone-700'
                            }`}
                    />
                ))}
            </div>
        </div>
    );
}
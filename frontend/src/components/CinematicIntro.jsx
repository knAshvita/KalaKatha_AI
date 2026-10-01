import React, { useEffect, useState } from 'react';
import { Sparkles, ArrowRight, Compass } from 'lucide-react';

export default function CinematicIntro({ onComplete }) {
    // Stages:
    // 0: Initial off-screen 3D preparation
    // 1: Collision ("Kala" & "Katha" slide from left & right with 3D tilt)
    // 2: Fusion (Light pulse + "AI" badge drops)
    // 3: Subtitle and "Enter Exhibition" CTA reveal
    // 4: Seamless fade out into main page
    const [animationStage, setAnimationStage] = useState(0);

    useEffect(() => {
        // Start sliding in immediately
        const t1 = setTimeout(() => setAnimationStage(1), 100);
        // Impact & fuse together at center
        const t2 = setTimeout(() => setAnimationStage(2), 1200);
        // Reveal poetic tagline & button
        const t3 = setTimeout(() => setAnimationStage(3), 2000);

        return () => {
            clearTimeout(t1);
            clearTimeout(t2);
            clearTimeout(t3);
        };
    }, []);

    const handleEnter = () => {
        setAnimationStage(4);
        setTimeout(() => {
            onComplete();
        }, 700); // Wait for dissolve animation to complete
    };

    return (
        <div
            className={`fixed inset-0 z-[100] flex flex-col items-center justify-center bg-stone-950 text-stone-100 overflow-hidden select-none transition-all duration-700 ease-in-out ${animationStage === 4 ? 'opacity-0 scale-105 pointer-events-none' : 'opacity-100 scale-100'
                }`}
            style={{ perspective: '1200px' }}
        >
            {/* Ambient Radial Museum Glow & Vignette */}
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(217,119,6,0.12)_0%,rgba(10,10,12,0.95)_75%)] pointer-events-none" />

            {/* Floating Canvas Dust Particles */}
            <div className="absolute inset-0 opacity-20 pointer-events-none">
                <div className="absolute top-1/4 left-1/5 w-72 h-72 bg-amber-600/20 rounded-full blur-3xl animate-pulse" />
                <div className="absolute bottom-1/4 right-1/5 w-80 h-80 bg-amber-700/15 rounded-full blur-3xl animate-pulse delay-700" />
            </div>

            <div className="relative z-10 flex flex-col items-center justify-center max-w-4xl px-4 text-center space-y-8">

                {/* Sanskrit Cultural Watermark Backdrop */}
                <div
                    className={`absolute text-7xl sm:text-9xl md:text-[13rem] font-serif font-bold text-amber-500/[0.04] pointer-events-none tracking-widest transition-all duration-1000 ${animationStage >= 2 ? 'opacity-100 scale-100' : 'opacity-0 scale-90'
                        }`}
                >
                    कलाकथा
                </div>

                {/* 3D Collision Stage: KALA (Left) + KATHA (Right) */}
                <div className="relative flex items-center justify-center flex-wrap sm:flex-nowrap gap-x-2 sm:gap-x-3 py-6">

                    {/* "Kala" Sliding from Left with 3D Y-axis tilt */}
                    <div
                        className={`transition-all duration-1000 ease-[cubic-bezier(0.25,1,0.5,1)] transform ${animationStage === 0
                                ? '-translate-x-[120vw] opacity-0 rotate-y-[45deg] scale-90'
                                : 'translate-x-0 opacity-100 rotate-y-0 scale-100'
                            }`}
                    >
                        <span className="font-serif text-6xl sm:text-8xl md:text-9xl font-bold tracking-tight bg-gradient-to-r from-amber-200 via-stone-100 to-amber-100 bg-clip-text text-transparent drop-shadow-[0_10px_20px_rgba(0,0,0,0.8)]">
                            Kala
                        </span>
                    </div>

                    {/* Center Fusion Sparkle Burst (triggers when they meet) */}
                    <div
                        className={`w-3 sm:w-4 transition-all duration-700 transform ${animationStage >= 2
                                ? 'scale-100 opacity-100 drop-shadow-[0_0_25px_rgba(245,158,11,0.9)]'
                                : 'scale-0 opacity-0'
                            }`}
                    >
                        <span className="w-2.5 h-2.5 rounded-full bg-amber-400 block mx-auto animate-ping" />
                    </div>

                    {/* "Katha" Sliding from Right with counter 3D Y-axis tilt */}
                    <div
                        className={`transition-all duration-1000 ease-[cubic-bezier(0.25,1,0.5,1)] transform ${animationStage === 0
                                ? 'translate-x-[120vw] opacity-0 -rotate-y-[45deg] scale-90'
                                : 'translate-x-0 opacity-100 rotate-y-0 scale-100'
                            }`}
                    >
                        <span className="font-serif text-6xl sm:text-8xl md:text-9xl font-bold tracking-tight text-amber-500 drop-shadow-[0_10px_25px_rgba(217,119,6,0.5)]">
                            Katha
                        </span>
                    </div>

                    {/* "AI" Pill Falling Softly from Above into Position */}
                    <div
                        className={`transition-all duration-700 delay-100 ease-out transform ${animationStage >= 2
                                ? 'translate-y-0 opacity-100 scale-100'
                                : '-translate-y-12 opacity-0 scale-50'
                            }`}
                    >
                        <span className="ml-1 sm:ml-3 px-3 py-1 sm:px-4 sm:py-1.5 rounded-2xl bg-gradient-to-br from-amber-500 to-amber-700 text-stone-950 font-sans font-bold text-xl sm:text-3xl tracking-widest uppercase shadow-[0_0_30px_rgba(245,158,11,0.5)] inline-block align-top">
                            AI
                        </span>
                    </div>
                </div>

                {/* Poetic Subtitle & Vision Reveal */}
                <div
                    className={`space-y-3 transition-all duration-1000 delay-200 transform ${animationStage >= 3
                            ? 'translate-y-0 opacity-100 filter blur-0'
                            : 'translate-y-6 opacity-0 filter blur-sm'
                        }`}
                >
                    <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs sm:text-sm font-medium tracking-widest uppercase">
                        <Sparkles className="w-3.5 h-3.5 text-amber-400 animate-spin" style={{ animationDuration: '6s' }} />
                        <span>Interactive Digital Museum Experience</span>
                    </div>

                    <p className="font-serif text-xl sm:text-2xl md:text-3xl italic text-stone-300 max-w-2xl mx-auto leading-relaxed">
                        “Don’t just look at art. Step inside it.”
                    </p>

                    <p className="text-xs sm:text-sm text-stone-400 font-sans tracking-wide max-w-lg mx-auto">
                        Where centuries of artistic heritage converse with multi-agent intelligence.
                    </p>
                </div>

                {/* Enter Exhibition CTA Button */}
                <div
                    className={`pt-6 transition-all duration-700 delay-300 transform ${animationStage >= 3 ? 'translate-y-0 opacity-100 scale-100' : 'translate-y-8 opacity-0 scale-90'
                        }`}
                >
                    <button
                        type="button"
                        onClick={handleEnter}
                        className="group relative inline-flex items-center gap-3 px-8 py-4 rounded-full bg-gradient-to-r from-amber-600 via-amber-500 to-amber-600 hover:from-amber-500 hover:to-amber-400 text-stone-950 font-sans font-semibold text-sm tracking-wider uppercase transition-all duration-300 shadow-[0_0_35px_rgba(217,119,6,0.4)] hover:shadow-[0_0_50px_rgba(245,158,11,0.7)] hover:scale-105 active:scale-95 cursor-pointer"
                    >
                        <Compass className="w-4 h-4 text-stone-950 group-hover:rotate-45 transition-transform duration-500" />
                        <span>Enter The Museum</span>
                        <ArrowRight className="w-4 h-4 text-stone-950 group-hover:translate-x-1.5 transition-transform duration-300" />
                    </button>

                    <div className="pt-3">
                        <span className="text-[11px] text-stone-400 font-mono tracking-wider opacity-60">
                            Click or press anywhere to enter
                        </span>
                    </div>
                </div>

            </div>

            {/* Subtle Bottom Progress Glow Ribbon */}
            <div className="absolute bottom-0 left-0 right-0 h-1 bg-stone-900">
                <div
                    className={`h-full bg-gradient-to-r from-amber-600 to-amber-400 transition-all duration-[3000ms] ease-out ${animationStage >= 1 ? 'w-full' : 'w-0'
                        }`}
                />
            </div>
        </div>
    );
}
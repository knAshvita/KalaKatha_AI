import React from 'react';
import { Sun, Moon, Eye, RotateCcw } from 'lucide-react';

const NAV_LINKS = [
    { label: 'Exhibition', id: 'gallery' },
    { label: 'Personas', id: 'guides' },
    { label: 'Upload', id: 'upload' },
    { label: 'Reflections', id: 'quotes' },
    { label: 'Masters', id: 'artists' },
    { label: 'About', id: 'about' },
];

export default function Navbar({
    darkMode,
    setDarkMode,
    highContrast,
    setHighContrast,
    onReset,
    hasArtwork
}) {
    const handleScrollToSection = (sectionId) => {
        // If viewing an artwork result, return to the main gallery first
        if (hasArtwork) {
            onReset();
            setTimeout(() => {
                scrollToTarget(sectionId);
            }, 100);
        } else {
            scrollToTarget(sectionId);
        }
    };

    const scrollToTarget = (id) => {
        const element = document.getElementById(id);
        if (element) {
            // Calculate offset to account for sticky navbar (70px)
            const navbarOffset = 70;
            const elementPosition = element.getBoundingClientRect().top;
            const offsetPosition = elementPosition + window.pageYOffset - navbarOffset;

            window.scrollTo({
                top: offsetPosition,
                behavior: 'smooth'
            });
        }
    };

    return (
        <header className="sticky top-0 z-50 backdrop-blur-md bg-white/90 dark:bg-stone-950/90 border-b border-stone-200/80 dark:border-stone-800/80 transition-colors select-none">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">

                {/* Left Side: Brand Logo & Title */}
                <div
                    className="flex items-center gap-3 cursor-pointer group flex-shrink-0"
                    onClick={onReset}
                >
                    <div className="w-10 h-10 rounded-full bg-stone-900 dark:bg-stone-100 text-white dark:text-stone-900 flex items-center justify-center font-serif text-lg font-bold shadow-sm group-hover:scale-105 transition-transform">
                        क
                    </div>
                    <div>
                        <div className="flex items-center gap-1.5">
                            <span className="font-serif text-lg sm:text-xl tracking-tight font-semibold text-stone-900 dark:text-stone-100">
                                KalaKatha
                            </span>
                            <span className="text-[10px] uppercase tracking-widest px-1.5 py-0.5 rounded-full bg-amber-100 dark:bg-amber-950/80 text-amber-900 dark:text-amber-200 font-sans font-semibold">
                                AI
                            </span>
                        </div>
                        <p className="text-[10px] text-stone-400 dark:text-stone-500 font-sans tracking-wide hidden sm:block">
                            Digital Museum Experience
                        </p>
                    </div>
                </div>

                {/* Right Side: Navigation Buttons + Theme/Accessibility Tools */}
                <div className="flex items-center gap-2 sm:gap-4">

                    {/* Navigation Links Aligned Right */}
                    {!hasArtwork && (
                        <nav className="hidden md:flex items-center gap-1 lg:gap-1.5 pr-2 border-r border-stone-200 dark:border-stone-800">
                            {NAV_LINKS.map((link) => (
                                <button
                                    key={link.id}
                                    type="button"
                                    onClick={() => handleScrollToSection(link.id)}
                                    className="px-3 py-1.5 rounded-full text-xs font-medium text-stone-600 dark:text-stone-400 hover:text-stone-900 dark:hover:text-stone-100 hover:bg-stone-100 dark:hover:bg-stone-800 transition-colors tracking-wide cursor-pointer focus:outline-none"
                                >
                                    {link.label}
                                </button>
                            ))}
                        </nav>
                    )}

                    {/* Action Tools */}
                    <div className="flex items-center gap-2 flex-shrink-0">
                        {hasArtwork && (
                            <button
                                onClick={onReset}
                                className="flex items-center gap-1.5 text-xs tracking-wider uppercase px-3 py-1.5 rounded-full bg-stone-100 dark:bg-stone-800 text-stone-700 dark:text-stone-200 hover:bg-stone-200 dark:hover:bg-stone-700 transition cursor-pointer"
                                title="Return to museum gallery"
                            >
                                <RotateCcw className="w-3.5 h-3.5" />
                                <span className="hidden sm:inline">New Artwork</span>
                            </button>
                        )}

                        <button
                            onClick={() => setHighContrast(!highContrast)}
                            aria-label="Toggle high contrast accessibility mode"
                            title="Toggle high contrast mode"
                            className={`p-2 rounded-full border transition cursor-pointer ${highContrast
                                    ? 'bg-amber-500 text-black border-amber-600 font-bold'
                                    : 'border-stone-200 dark:border-stone-800 text-stone-600 dark:text-stone-300 hover:bg-stone-100 dark:hover:bg-stone-800'
                                }`}
                        >
                            <Eye className="w-4 h-4" />
                        </button>

                        <button
                            onClick={() => setDarkMode(!darkMode)}
                            aria-label="Toggle dark / light theme"
                            title="Toggle theme"
                            className="p-2 rounded-full border border-stone-200 dark:border-stone-800 text-stone-600 dark:text-stone-300 hover:bg-stone-100 dark:hover:bg-stone-800 transition cursor-pointer"
                        >
                            {darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
                        </button>
                    </div>

                </div>

            </div>
        </header>
    );
}
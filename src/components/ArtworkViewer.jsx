import React, { useState } from 'react';
import { Maximize2, Minimize2, ZoomIn, ZoomOut, RotateCcw, Palette } from 'lucide-react';

// Maps raw color names to hex codes for the swatches if hex isn't provided
const COLOR_HEX_MAP = {
    "Cobalt Blue": "#1d4ed8",
    "Ultramarine": "#1e3a8a",
    "Zinc White": "#f8fafc",
    "Indian Yellow": "#eab308",
    "Viridian Deep": "#065f46",
    "Ultramarine Blue": "#1e40af",
    "Lead Tin Yellow": "#fef08a",
    "Bone Black": "#18181b",
    "Alizarin Crimson": "#991b1b",
    "Pearl Luster White": "#f1f5f9",
    "Burnt Umber": "#451a03",
    "Terra Verde": "#3f6212",
    "Raw Sienna": "#b45309",
    "Atmospheric Haze Gray": "#94a3b8",
    "Muted Olive": "#65a30d",
    "Prussian Blue": "#0c4a6e",
    "Indigo": "#312e81",
    "Pale Ochre": "#fde047",
    "Bokashi Sky Gray": "#cbd5e1",
    "Sea Foam White": "#f0fdf4",
    "Slate Gray": "#64748b",
    "Vapour Blue": "#bfdbfe",
    "Forest Shadow Green": "#14532d",
    "Mist White": "#f8fafc",
    "Charcoal Black": "#27272a",
    "Emerald Green": "#059669",
    "Lavender Violet": "#a855f7",
    "Pale Rose": "#fda4af",
    "Cerulean Blue": "#0284c7",
    "Sunlit Primrose": "#fef08a",
    "Burnished Gold Leaf": "#d97706",
    "Bronze Ochre": "#92400e",
    "Meadow Green": "#16a34a",
    "Lavender": "#c084fc",
    "Poppy Crimson": "#dc2626"
};

export default function ArtworkViewer({
    imageSrc,
    title = "Selected Artwork",
    activeFocus = null,
    colors = []
}) {
    const [scale, setScale] = useState(1);
    const [isFullscreen, setIsFullscreen] = useState(false);

    const handleZoomIn = () => setScale((prev) => Math.min(prev + 0.25, 2.5));
    const handleZoomOut = () => setScale((prev) => Math.max(prev - 0.25, 1));
    const handleResetZoom = () => setScale(1);

    // Focus positioning helper for guided storytelling
    const getFocusStyle = () => {
        switch (activeFocus) {
            case 'top':
                return { transform: `scale(${scale}) translateY(12%)` };
            case 'bottom':
                return { transform: `scale(${scale}) translateY(-12%)` };
            case 'left':
                return { transform: `scale(${scale}) translateX(12%)` };
            case 'right':
                return { transform: `scale(${scale}) translateX(-12%)` };
            case 'center':
                return { transform: `scale(${scale * 1.1})` };
            default:
                return { transform: `scale(${scale})` };
        }
    };

    const getSwatchColor = (colorName) => {
        if (typeof colorName === 'string' && colorName.startsWith('#')) return colorName;
        return COLOR_HEX_MAP[colorName] || '#78716c';
    };

    return (
        <div
            className={`relative rounded-3xl overflow-hidden bg-stone-950 border border-stone-800 shadow-2xl transition-all duration-500 select-none ${isFullscreen ? 'fixed inset-0 z-50 rounded-none' : 'w-full aspect-[4/3] sm:aspect-[16/11]'
                }`}
        >
            {/* 1. Canvas Viewport */}
            <div className="w-full h-full flex items-center justify-center overflow-hidden bg-black/95">
                <img
                    src={imageSrc}
                    alt={title}
                    referrerPolicy="no-referrer"
                    className="max-h-full max-w-full object-contain transition-transform duration-700 ease-out will-change-transform"
                    style={getFocusStyle()}
                    draggable={false}
                />
            </div>

            {/* 2. Top Controls Ribbon */}
            <div className="absolute top-4 right-4 z-20 flex items-center gap-1.5 p-1.5 rounded-full bg-black/60 backdrop-blur-md border border-white/10 text-white">
                <button
                    type="button"
                    onClick={handleZoomIn}
                    className="p-1.5 rounded-full hover:bg-white/20 transition active:scale-95 cursor-pointer"
                    title="Zoom In"
                >
                    <ZoomIn className="w-4 h-4" />
                </button>
                <button
                    type="button"
                    onClick={handleZoomOut}
                    className="p-1.5 rounded-full hover:bg-white/20 transition active:scale-95 cursor-pointer"
                    title="Zoom Out"
                >
                    <ZoomOut className="w-4 h-4" />
                </button>
                {scale !== 1 && (
                    <button
                        type="button"
                        onClick={handleResetZoom}
                        className="p-1.5 rounded-full hover:bg-white/20 transition active:scale-95 cursor-pointer text-amber-400"
                        title="Reset Zoom"
                    >
                        <RotateCcw className="w-4 h-4" />
                    </button>
                )}
                <button
                    type="button"
                    onClick={() => setIsFullscreen(!isFullscreen)}
                    className="p-1.5 rounded-full hover:bg-white/20 transition active:scale-95 cursor-pointer"
                    title={isFullscreen ? "Exit Fullscreen" : "Fullscreen View"}
                >
                    {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
                </button>
            </div>

            {/* 3. Bottom Scrim: Title & Clearly Labeled Pigment Palette */}
            <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/95 via-black/60 to-transparent p-5 sm:p-6 flex flex-col sm:flex-row sm:items-end justify-between gap-3 text-white z-20">
                <div>
                    <h2 className="font-serif text-xl sm:text-2xl font-bold tracking-tight">
                        {title}
                    </h2>
                    <p className="text-xs text-amber-300/90 font-sans tracking-wide mt-0.5">
                        Digital Artifact Stage • Archival Multi-Agent Scan
                    </p>
                </div>

                {/* Labeled Master Palette Swatches */}
                {colors && colors.length > 0 && (
                    <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-black/60 backdrop-blur-md border border-white/10">
                        <Palette className="w-3.5 h-3.5 text-amber-400" />
                        <span className="text-[10px] uppercase tracking-wider text-stone-300 font-semibold hidden sm:inline">
                            Palette:
                        </span>
                        <div className="flex items-center gap-1.5">
                            {colors.map((c, i) => {
                                const swatchBg = getSwatchColor(c);
                                return (
                                    <span
                                        key={i}
                                        className="w-3.5 h-3.5 rounded-full border border-white/40 shadow-xs cursor-pointer hover:scale-135 transition-transform"
                                        style={{ backgroundColor: swatchBg }}
                                        title={c}
                                    />
                                );
                            })}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
import React, { useState } from 'react';
import { Maximize2, Minimize2, ZoomIn, ZoomOut, RotateCcw, Palette, Target, X, Info } from 'lucide-react';

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
    "Poppy Crimson": "#dc2626",
    "Gold": "#eab308",
    "Crimson": "#b91c1c",
    "Vermilion": "#ea580c",
    "Ochre": "#d97706",
    "White": "#f8fafc",
    "Black": "#18181b"
};

export default function ArtworkViewer({
    imageSrc,
    title = "Selected Artwork",
    artist = null,
    period = null,
    activeFocus = null,
    colors = [],
    regions = []
}) {
    const [scale, setScale] = useState(1);
    const [isFullscreen, setIsFullscreen] = useState(false);
    const [showHotspots, setShowHotspots] = useState(true);
    const [activeRegion, setActiveRegion] = useState(null);

    const handleZoomIn = () => setScale((prev) => Math.min(prev + 0.25, 2.5));
    const handleZoomOut = () => setScale((prev) => Math.max(prev - 0.25, 1));
    const handleResetZoom = () => {
        setScale(1);
        setActiveRegion(null);
    };

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

    // Normalize colors whether passed as string or array
    const colorList = Array.isArray(colors)
        ? colors
        : (typeof colors === 'string'
            ? colors.split(',').map(s => s.trim()).filter(Boolean)
            : []);

    const getSwatchColor = (colorName) => {
        if (!colorName) return '#78716c';
        if (typeof colorName === 'string' && colorName.startsWith('#')) return colorName;
        // Check map or fuzzy find
        const lower = colorName.toLowerCase();
        for (const [key, val] of Object.entries(COLOR_HEX_MAP)) {
            if (lower.includes(key.toLowerCase())) return val;
        }
        return '#b45309';
    };

    return (
        <div
            className={`relative rounded-3xl overflow-hidden bg-stone-950 border border-stone-800 shadow-2xl transition-all duration-500 select-none ${
                isFullscreen ? 'fixed inset-0 z-50 rounded-none' : 'w-full aspect-[4/3] sm:aspect-[16/11]'
            }`}
        >
            {/* 1. Canvas Viewport */}
            <div className="w-full h-full relative flex items-center justify-center overflow-hidden bg-black/95">
                <img
                    src={imageSrc}
                    alt={title}
                    referrerPolicy="no-referrer"
                    className="max-h-full max-w-full object-contain transition-transform duration-700 ease-out will-change-transform"
                    style={getFocusStyle()}
                    draggable={false}
                />

                {/* Interactive Hotspot Overlay */}
                {showHotspots && regions && regions.length > 0 && scale === 1 && (
                    <div className="absolute inset-0 pointer-events-none flex items-center justify-center">
                        <div className="relative w-full h-full max-h-full max-w-full">
                            {regions.map((region, idx) => {
                                const pos = region.position || { x: 0.5, y: 0.5, width: 0.1, height: 0.1 };
                                const leftPercent = Math.max(5, Math.min(90, (pos.x || 0.4) * 100));
                                const topPercent = Math.max(5, Math.min(85, (pos.y || 0.4) * 100));
                                const isSelected = activeRegion?.region_id === region.region_id;

                                return (
                                    <div
                                        key={region.region_id || idx}
                                        style={{ left: `${leftPercent}%`, top: `${topPercent}%` }}
                                        className="absolute pointer-events-auto transform -translate-x-1/2 -translate-y-1/2 z-20 group"
                                    >
                                        <button
                                            type="button"
                                            onClick={() => setActiveRegion(isSelected ? null : region)}
                                            className={`relative flex items-center justify-center w-7 h-7 sm:w-8 sm:h-8 rounded-full border-2 transition-all duration-300 shadow-lg cursor-pointer ${
                                                isSelected
                                                    ? 'bg-amber-500 border-white text-stone-950 scale-125 ring-4 ring-amber-400/40'
                                                    : 'bg-black/75 hover:bg-amber-600 border-amber-400 text-amber-200 hover:text-white hover:scale-115'
                                            }`}
                                            title={region.label || `Region ${idx + 1}`}
                                        >
                                            <span className="text-[11px] font-bold">{idx + 1}</span>
                                            {/* Pulsing ring */}
                                            <span className="absolute -inset-1 rounded-full bg-amber-400/30 animate-ping pointer-events-none" />
                                        </button>

                                        {/* Hover Tag */}
                                        {!isSelected && (
                                            <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1.5 hidden group-hover:block whitespace-nowrap px-2.5 py-1 rounded-md bg-stone-900/90 text-amber-200 text-[10px] font-medium border border-amber-500/30 backdrop-blur-sm pointer-events-none shadow-md">
                                                {region.label}
                                            </div>
                                        )}
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                )}

                {/* Selected Region Detailed Floating Card */}
                {activeRegion && (
                    <div className="absolute top-16 left-4 right-4 sm:right-auto sm:max-w-sm z-30 p-4 rounded-2xl bg-stone-900/95 border border-amber-500/40 backdrop-blur-md shadow-2xl text-white animate-fade-in space-y-2">
                        <div className="flex items-start justify-between gap-2">
                            <div className="flex items-center gap-1.5 text-amber-400 text-xs font-semibold uppercase tracking-wider">
                                <Target className="w-3.5 h-3.5" />
                                <span>{activeRegion.importance || "Focal Hotspot"}</span>
                            </div>
                            <button
                                type="button"
                                onClick={() => setActiveRegion(null)}
                                className="p-1 rounded-full hover:bg-stone-800 text-stone-400 hover:text-white transition"
                            >
                                <X className="w-3.5 h-3.5" />
                            </button>
                        </div>
                        <h4 className="font-serif text-base font-bold text-stone-100">{activeRegion.label}</h4>
                        <p className="text-xs text-stone-300 leading-relaxed font-serif">{activeRegion.description}</p>
                        {activeRegion.related_visual_elements && activeRegion.related_visual_elements.length > 0 && (
                            <div className="flex flex-wrap gap-1 pt-1">
                                {activeRegion.related_visual_elements.map((el, i) => (
                                    <span key={i} className="text-[10px] px-2 py-0.5 rounded-md bg-stone-800 text-amber-200 border border-stone-700">
                                        {el}
                                    </span>
                                ))}
                            </div>
                        )}
                    </div>
                )}
            </div>

            {/* 2. Top Controls Ribbon */}
            <div className="absolute top-4 right-4 z-20 flex items-center gap-1.5 p-1.5 rounded-full bg-black/60 backdrop-blur-md border border-white/10 text-white shadow-lg">
                {regions && regions.length > 0 && (
                    <button
                        type="button"
                        onClick={() => setShowHotspots(!showHotspots)}
                        className={`p-1.5 rounded-full transition active:scale-95 cursor-pointer ${
                            showHotspots ? 'bg-amber-600 text-white' : 'hover:bg-white/20 text-stone-300'
                        }`}
                        title={showHotspots ? "Hide Hotspots" : "Show Hotspots"}
                    >
                        <Target className="w-4 h-4" />
                    </button>
                )}
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

            {/* 3. Bottom Scrim: Title, Artist, Period & Labeled Pigment Palette */}
            <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/95 via-black/60 to-transparent p-5 sm:p-6 flex flex-col sm:flex-row sm:items-end justify-between gap-3 text-white z-20">
                <div>
                    <h2 className="font-serif text-xl sm:text-2xl font-bold tracking-tight">
                        {title}
                    </h2>
                    <p className="text-xs text-amber-300/90 font-sans tracking-wide mt-0.5">
                        {artist ? `${artist}` : 'Archival Multi-Agent Scan'} {period ? `• ${period}` : ''}
                    </p>
                </div>

                {/* Labeled Master Palette Swatches */}
                {colorList && colorList.length > 0 && (
                    <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-black/60 backdrop-blur-md border border-white/10">
                        <Palette className="w-3.5 h-3.5 text-amber-400" />
                        <span className="text-[10px] uppercase tracking-wider text-stone-300 font-semibold hidden sm:inline">
                            Palette:
                        </span>
                        <div className="flex items-center gap-1.5">
                            {colorList.slice(0, 7).map((c, i) => {
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
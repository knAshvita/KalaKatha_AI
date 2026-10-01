import React from 'react';
import {
    Eye,
    Layers,
    BookOpen,
    GraduationCap,
    Sparkles,
    Smile,
    Compass,
    Quote,
    Building2,
    Calendar,
    MapPin,
    Award,
    Sun,
    Accessibility,
    Check
} from 'lucide-react';

const GUIDE_OPTIONS = [
    { id: 'professor', title: 'Professor', icon: GraduationCap, tag: 'Academic Critique', desc: 'Curatorial depth & lineage' },
    { id: 'storyteller', title: 'Storyteller', icon: Sparkles, tag: 'Evocative Prose', desc: 'Cinematic museum tale' },
    { id: 'friendly', title: 'Friendly Guide', icon: Smile, tag: 'Fun Curiosities', desc: 'Warm conversational companion' },
    { id: 'accessibility', title: 'Accessibility Guide', icon: Compass, tag: 'Spatial Layout', desc: '8-zone layout & sensory audio' }
];

export default function ExploreTab({
    visualAnalysis,
    context,
    accessibility,
    personaNotes,
    selectedGuide,
    onSelectGuide,
    artistProfile
}) {
    const activeGuideObj = GUIDE_OPTIONS.find((g) => g.id === selectedGuide) || GUIDE_OPTIONS[0];

    // Helper to extract clean text from either a string or an array of ContextFact
    const renderContextFacts = (factsOrString) => {
        if (!factsOrString) return null;
        if (typeof factsOrString === 'string') {
            return <p className="text-sm font-serif leading-relaxed text-stone-700 dark:text-stone-300">{factsOrString}</p>;
        }
        if (Array.isArray(factsOrString)) {
            return (
                <div className="space-y-2">
                    {factsOrString.map((item, idx) => {
                        const claim = typeof item === 'object' && item !== null ? item.claim : String(item);
                        const certainty = typeof item === 'object' && item !== null ? item.certainty : null;
                        const basis = typeof item === 'object' && item !== null ? item.basis : null;

                        return (
                            <div key={idx} className="space-y-0.5">
                                <div className="flex items-start gap-2">
                                    <span className="text-amber-600 font-bold mt-0.5">•</span>
                                    <div className="text-xs sm:text-sm font-serif leading-relaxed text-stone-700 dark:text-stone-300">
                                        <span>{claim}</span>
                                        {certainty && (
                                            <span className="ml-2 text-[9px] uppercase tracking-wider px-1.5 py-0.5 rounded bg-stone-100 dark:bg-stone-800 text-stone-500 font-sans font-semibold">
                                                {certainty}
                                            </span>
                                        )}
                                    </div>
                                </div>
                                {basis && (
                                    <p className="text-[11px] text-stone-400 dark:text-stone-500 pl-4 font-sans italic">
                                        Basis: {basis}
                                    </p>
                                )}
                            </div>
                        );
                    })}
                </div>
            );
        }
        return null;
    };

    // Synthesize persona perspective text
    const getPersonaQuote = () => {
        if (personaNotes && personaNotes[selectedGuide]) {
            return personaNotes[selectedGuide];
        }
        switch (selectedGuide) {
            case 'professor':
                return `Formal composition analysis indicates rigorous attention to ${visualAnalysis?.perspective || 'geometric perspective'} and ${visualAnalysis?.lighting || 'tonal contrast'}.`;
            case 'friendly':
                return `Take a close look at the central visual focus: ${visualAnalysis?.visual_focus || 'the depicted subjects'}. It completely sets the mood!`;
            case 'accessibility':
                return accessibility?.accessibility_description || `Centering around ${visualAnalysis?.visual_focus || 'the main subjects'}, with rich spatial depth across foreground and background.`;
            case 'storyteller':
            default:
                return visualAnalysis?.summary || "An evocative examination of brushcraft, light, and cultural symbolism.";
        }
    };

    return (
        <div className="space-y-6 animate-fade-in text-stone-800 dark:text-stone-200">

            {/* ========================================================= */}
            {/* 1. ARTIST PROFILE (IF PRELOADED OR RECOGNIZED)            */}
            {/* ========================================================= */}
            {artistProfile && (
                <div className="p-6 rounded-3xl border border-amber-300/80 dark:border-amber-900/60 bg-gradient-to-br from-amber-50/60 via-white to-amber-50/20 dark:from-stone-900 dark:to-stone-950 shadow-sm space-y-4">
                    <div className="flex items-center justify-between">
                        <span className="text-[10px] uppercase tracking-widest font-bold text-amber-700 dark:text-amber-400 bg-amber-100 dark:bg-amber-950/70 px-2.5 py-0.5 rounded-full border border-amber-300 dark:border-amber-800">
                            Master Author Archive
                        </span>
                        <span className="text-xs text-stone-500 dark:text-stone-400 font-medium">
                            {artistProfile.movement || visualAnalysis?.style}
                        </span>
                    </div>

                    <div>
                        <h3 className="font-serif text-2xl sm:text-3xl font-bold text-stone-900 dark:text-stone-100">
                            {artistProfile.name}
                        </h3>
                        <div className="flex flex-wrap gap-4 text-xs text-stone-500 dark:text-stone-400 font-medium mt-1">
                            {artistProfile.years && (
                                <span className="flex items-center gap-1.5">
                                    <Calendar className="w-3.5 h-3.5 text-amber-600" />
                                    {artistProfile.years}
                                </span>
                            )}
                            {artistProfile.origin && (
                                <span className="flex items-center gap-1.5">
                                    <MapPin className="w-3.5 h-3.5 text-amber-600" />
                                    {artistProfile.origin}
                                </span>
                            )}
                        </div>
                    </div>

                    <p className="text-sm font-serif leading-relaxed text-stone-700 dark:text-stone-300">
                        {artistProfile.description || artistProfile.biography}
                    </p>
                </div>
            )}

            {/* ========================================================= */}
            {/* 2. VISUAL OBSERVATION & DETECTED ELEMENTS                 */}
            {/* ========================================================= */}
            <div className="p-6 rounded-3xl border border-stone-200/90 dark:border-stone-800 bg-white dark:bg-stone-900 shadow-xs space-y-4">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-amber-700 dark:text-amber-400 text-xs uppercase tracking-widest font-bold">
                        <Eye className="w-4 h-4 text-amber-600" />
                        <span>Visual Observations</span>
                    </div>
                    {visualAnalysis?.mood && (
                        <span className="text-[11px] text-stone-500 dark:text-stone-400 italic font-serif">
                            Mood: {visualAnalysis.mood}
                        </span>
                    )}
                </div>

                {visualAnalysis?.summary && (
                    <p className="text-sm font-serif leading-relaxed text-stone-700 dark:text-stone-300">
                        {visualAnalysis.summary}
                    </p>
                )}

                {/* Detected Objects Pills */}
                {visualAnalysis?.objects && visualAnalysis.objects.length > 0 && (
                    <div className="space-y-1.5 pt-1">
                        <span className="text-[10px] uppercase tracking-wider font-semibold text-stone-400 block">
                            Visible Elements:
                        </span>
                        <div className="flex flex-wrap gap-1.5">
                            {visualAnalysis.objects.map((obj, i) => (
                                <span
                                    key={i}
                                    className="text-xs font-medium px-3 py-1 rounded-lg bg-stone-100 dark:bg-stone-800/90 text-stone-700 dark:text-stone-300 border border-stone-200/60 dark:border-stone-700/60"
                                >
                                    {obj}
                                </span>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            {/* ========================================================= */}
            {/* 3. STYLE, LIGHTING & COMPOSITION                         */}
            {/* ========================================================= */}
            <div className="p-6 rounded-3xl border border-stone-200/90 dark:border-stone-800 bg-white dark:bg-stone-900 shadow-xs space-y-3">
                <div className="flex items-center gap-2 text-amber-700 dark:text-amber-400 text-xs uppercase tracking-widest font-bold">
                    <Layers className="w-4 h-4 text-amber-600" />
                    <span>Style & Composition</span>
                </div>

                <div className="space-y-2.5 text-xs leading-relaxed text-stone-600 dark:text-stone-300 font-serif">
                    {visualAnalysis?.style && (
                        <p>
                            <strong className="text-stone-900 dark:text-stone-100 font-sans font-semibold">Art Movement / Style:</strong> {visualAnalysis.style}
                        </p>
                    )}
                    {visualAnalysis?.composition && (
                        <p>
                            <strong className="text-stone-900 dark:text-stone-100 font-sans font-semibold">Composition:</strong> {visualAnalysis.composition}
                        </p>
                    )}
                    {visualAnalysis?.lighting && (
                        <p>
                            <strong className="text-stone-900 dark:text-stone-100 font-sans font-semibold">Lighting & Shadow:</strong> {visualAnalysis.lighting}
                        </p>
                    )}
                    {visualAnalysis?.visual_focus && (
                        <p>
                            <strong className="text-stone-900 dark:text-stone-100 font-sans font-semibold">Primary Focal Anchor:</strong> {visualAnalysis.visual_focus}
                        </p>
                    )}
                </div>
            </div>

            {/* ========================================================= */}
            {/* 4. HISTORICAL, CULTURAL CONTEXT & SYMBOLISM               */}
            {/* ========================================================= */}
            <div className="p-6 rounded-3xl border border-stone-200/90 dark:border-stone-800 bg-white dark:bg-stone-900 shadow-xs space-y-4">
                <div className="flex items-center gap-2 text-amber-700 dark:text-amber-400 text-xs uppercase tracking-widest font-bold">
                    <BookOpen className="w-4 h-4 text-amber-600" />
                    <span>Historical & Cultural Context</span>
                </div>

                {renderContextFacts(context?.historical_context)}

                {context?.symbolism && (
                    <div className="border-t border-stone-100 dark:border-stone-800 pt-3 space-y-1.5">
                        <span className="text-[11px] uppercase tracking-wider font-semibold text-stone-500 dark:text-stone-400 block">
                            Iconography & Symbolism:
                        </span>
                        {renderContextFacts(context.symbolism)}
                    </div>
                )}

                {context?.artistic_techniques && (
                    <div className="border-t border-stone-100 dark:border-stone-800 pt-3 space-y-1.5">
                        <span className="text-[11px] uppercase tracking-wider font-semibold text-stone-500 dark:text-stone-400 block">
                            Artistic Techniques:
                        </span>
                        {renderContextFacts(context.artistic_techniques)}
                    </div>
                )}
            </div>

            {/* ========================================================= */}
            {/* 5. ACCESSIBILITY & SPATIAL MENTAL MODEL                  */}
            {/* ========================================================= */}
            {accessibility && (
                <div className="p-6 rounded-3xl border border-amber-300/60 dark:border-amber-900/40 bg-amber-50/40 dark:bg-amber-950/20 shadow-xs space-y-3">
                    <div className="flex items-center gap-2 text-amber-800 dark:text-amber-300 text-xs uppercase tracking-widest font-bold">
                        <Accessibility className="w-4 h-4 text-amber-600" />
                        <span>Spatial Navigation & Accessibility</span>
                    </div>

                    {accessibility.accessibility_description && (
                        <p className="text-xs sm:text-sm font-serif leading-relaxed text-stone-700 dark:text-stone-300">
                            {accessibility.accessibility_description}
                        </p>
                    )}

                    {accessibility.spatial_description && (
                        <div className="grid grid-cols-2 gap-2 pt-2 text-[11px] font-serif text-stone-600 dark:text-stone-300">
                            {accessibility.spatial_description.center && (
                                <div className="p-2 rounded-lg bg-white/70 dark:bg-stone-900/60 border border-stone-200/60 dark:border-stone-800">
                                    <strong className="font-sans font-semibold text-amber-700 dark:text-amber-400 block">Center:</strong>
                                    {accessibility.spatial_description.center}
                                </div>
                            )}
                            {accessibility.spatial_description.foreground && (
                                <div className="p-2 rounded-lg bg-white/70 dark:bg-stone-900/60 border border-stone-200/60 dark:border-stone-800">
                                    <strong className="font-sans font-semibold text-amber-700 dark:text-amber-400 block">Foreground:</strong>
                                    {accessibility.spatial_description.foreground}
                                </div>
                            )}
                            {accessibility.spatial_description.background && (
                                <div className="p-2 rounded-lg bg-white/70 dark:bg-stone-900/60 border border-stone-200/60 dark:border-stone-800">
                                    <strong className="font-sans font-semibold text-amber-700 dark:text-amber-400 block">Background:</strong>
                                    {accessibility.spatial_description.background}
                                </div>
                            )}
                            {accessibility.spatial_description.relationships && (
                                <div className="p-2 rounded-lg bg-white/70 dark:bg-stone-900/60 border border-stone-200/60 dark:border-stone-800">
                                    <strong className="font-sans font-semibold text-amber-700 dark:text-amber-400 block">Spatial Layout:</strong>
                                    {accessibility.spatial_description.relationships}
                                </div>
                            )}
                        </div>
                    )}
                </div>
            )}

            {/* ========================================================= */}
            {/* 6. GUIDE PERSONA PERSPECTIVE CARD                         */}
            {/* ========================================================= */}
            {onSelectGuide && (
                <div className="p-6 rounded-3xl border border-amber-300/80 dark:border-amber-900/60 bg-gradient-to-br from-amber-50/70 via-white to-amber-50/30 dark:from-stone-900 dark:via-stone-900 dark:to-amber-950/20 shadow-sm space-y-4">
                    <div className="flex items-center justify-between flex-wrap gap-2">
                        <div className="flex items-center gap-2 text-xs uppercase tracking-widest font-bold text-amber-800 dark:text-amber-300">
                            <activeGuideObj.icon className="w-4 h-4 text-amber-600" />
                            <span>Guide Mode: {activeGuideObj.title}</span>
                        </div>
                        <span className="text-[11px] text-stone-500 dark:text-stone-400 italic font-serif">
                            {activeGuideObj.tag}
                        </span>
                    </div>

                    {/* Persona Toggle Grid */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                        {GUIDE_OPTIONS.map((g) => {
                            const Icon = g.icon;
                            const isSelected = selectedGuide === g.id;

                            return (
                                <button
                                    key={g.id}
                                    type="button"
                                    onClick={() => onSelectGuide(g.id)}
                                    className={`p-2.5 rounded-xl border text-left transition-all duration-300 cursor-pointer flex flex-col gap-0.5 ${
                                        isSelected
                                            ? 'border-amber-600 bg-amber-600 text-white shadow-md'
                                            : 'border-stone-200 dark:border-stone-800 bg-white dark:bg-stone-800/80 text-stone-700 dark:text-stone-300 hover:border-amber-400'
                                    }`}
                                >
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-1.5">
                                            <Icon className="w-3.5 h-3.5" />
                                            <span className="text-xs font-semibold">{g.title}</span>
                                        </div>
                                        {isSelected && <Check className="w-3 h-3 text-white" />}
                                    </div>
                                    <span className={`text-[10px] ${isSelected ? 'text-amber-100' : 'text-stone-400'}`}>
                                        {g.tag}
                                    </span>
                                </button>
                            );
                        })}
                    </div>

                    {/* Perspective Quote Card */}
                    <div className="p-4 rounded-2xl border border-amber-200/90 dark:border-amber-900/40 bg-white/90 dark:bg-stone-950/60 relative">
                        <Quote className="w-5 h-5 text-amber-600/30 absolute top-3 left-3 rotate-180" />
                        <div className="pl-6 space-y-1">
                            <span className="text-[10px] uppercase tracking-wider font-bold text-amber-700 dark:text-amber-400 block">
                                {activeGuideObj.title}’s Perspective
                            </span>
                            <p className="font-serif text-xs sm:text-sm text-stone-800 dark:text-stone-100 italic leading-relaxed">
                                “{getPersonaQuote()}”
                            </p>
                        </div>
                    </div>
                </div>
            )}

        </div>
    );
}
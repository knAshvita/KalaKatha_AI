import React from 'react';
import { Eye, Layers, BookOpen, GraduationCap, Sparkles, Smile, Compass, Quote, Building2, Calendar, MapPin, Award } from 'lucide-react';

const GUIDE_OPTIONS = [
    { id: 'professor', title: 'Professor', icon: GraduationCap, tag: 'Academic Critique' },
    { id: 'storyteller', title: 'Storyteller', icon: Sparkles, tag: 'Evocative Prose' },
    { id: 'friendly', title: 'Friendly Guide', icon: Smile, tag: 'Fun Curiosities' },
    { id: 'accessibility', title: 'Accessibility Guide', icon: Compass, tag: 'Spatial Layout' }
];

export default function ExploreTab({ visualAnalysis, context, personaNotes, selectedGuide, onSelectGuide, artistProfile }) {
    const currentPersonaText = personaNotes?.[selectedGuide] || personaNotes?.['storyteller'] || "An evocative examination of brushcraft and cultural symbolism.";
    const activeGuideObj = GUIDE_OPTIONS.find(g => g.id === selectedGuide) || GUIDE_OPTIONS[0];

    return (
        <div className="space-y-6 animate-fade-in text-stone-800 dark:text-stone-200">

            {/* ========================================================= */}
            {/* 1. AUTHOR / ARTIST VIEW: PURE AUTHOR PROFILE (NO PERSONAS) */}
            {/* ========================================================= */}
            {artistProfile && (
                <div className="p-6 rounded-2xl border border-amber-300/80 dark:border-amber-900/60 bg-gradient-to-br from-amber-50/60 via-white to-amber-50/20 dark:from-stone-900 dark:to-stone-950 shadow-sm space-y-5">
                    <div className="flex items-center justify-between">
                        <span className="text-[10px] uppercase tracking-widest font-bold text-amber-700 dark:text-amber-400 bg-amber-100 dark:bg-amber-950/70 px-2.5 py-0.5 rounded-full border border-amber-300 dark:border-amber-800">
                            Master Author Archive
                        </span>
                        <span className="text-xs text-stone-500 dark:text-stone-400 font-medium">
                            {artistProfile.movement}
                        </span>
                    </div>

                    <div>
                        <h3 className="font-serif text-3xl font-bold text-stone-900 dark:text-stone-100">
                            {artistProfile.name}
                        </h3>
                        <div className="flex flex-wrap gap-4 text-xs text-stone-500 dark:text-stone-400 font-medium mt-1.5">
                            <span className="flex items-center gap-1.5">
                                <Calendar className="w-3.5 h-3.5 text-amber-600" />
                                {artistProfile.years}
                            </span>
                            <span className="flex items-center gap-1.5">
                                <MapPin className="w-3.5 h-3.5 text-amber-600" />
                                {artistProfile.origin}
                            </span>
                        </div>
                    </div>

                    {/* Full Biography */}
                    <div className="space-y-1.5 pt-1">
                        <span className="text-[11px] uppercase tracking-wider font-semibold text-stone-500 dark:text-stone-400">
                            Author Biography & Legacy
                        </span>
                        <p className="text-sm font-serif leading-relaxed text-stone-700 dark:text-stone-300">
                            {artistProfile.description || artistProfile.biography}
                        </p>
                    </div>

                    {/* Masterpiece & Museum Location Box */}
                    <div className="p-4 rounded-xl bg-white dark:bg-stone-800/90 border border-stone-200/80 dark:border-stone-700 space-y-2 text-xs">
                        <div className="flex items-center gap-2 text-amber-800 dark:text-amber-300 font-semibold text-sm">
                            <Award className="w-4 h-4 text-amber-600 flex-shrink-0" />
                            <span>Highest Acclaimed Art: {artistProfile.famousWork?.title} ({artistProfile.famousWork?.year})</span>
                        </div>
                        <div className="flex items-center gap-2 text-stone-600 dark:text-stone-300">
                            <Building2 className="w-4 h-4 text-stone-500 flex-shrink-0" />
                            <span>Preserved at: <strong>{artistProfile.famousWork?.museum}</strong></span>
                        </div>
                    </div>
                </div>
            )}

            {/* ========================================================= */}
            {/* 2. CORE ARTWORK DATA (DETECTED ELEMENTS)                  */}
            {/* ========================================================= */}
            <div className="p-5 rounded-2xl border border-stone-200/90 dark:border-stone-800 bg-white dark:bg-stone-900 shadow-xs space-y-3">
                <div className="flex items-center gap-2 text-amber-700 dark:text-amber-400 text-xs uppercase tracking-widest font-semibold">
                    <Eye className="w-4 h-4 text-amber-600" />
                    <span>Detected Elements</span>
                </div>
                <div className="flex flex-wrap gap-2 pt-1">
                    {visualAnalysis?.objects?.map((obj, i) => (
                        <span
                            key={i}
                            className="text-xs font-medium px-3 py-1.5 rounded-lg bg-stone-100 dark:bg-stone-800/90 text-stone-700 dark:text-stone-300 border border-stone-200/60 dark:border-stone-700/60 shadow-2xs"
                        >
                            {obj}
                        </span>
                    ))}
                </div>
            </div>

            {/* ========================================================= */}
            {/* 3. STYLE & COMPOSITION                                    */}
            {/* ========================================================= */}
            <div className="p-5 rounded-2xl border border-stone-200/90 dark:border-stone-800 bg-white dark:bg-stone-900 shadow-xs space-y-3">
                <div className="flex items-center gap-2 text-amber-700 dark:text-amber-400 text-xs uppercase tracking-widest font-semibold">
                    <Layers className="w-4 h-4 text-amber-600" />
                    <span>Style & Composition</span>
                </div>
                <div className="space-y-2 text-xs leading-relaxed text-stone-600 dark:text-stone-300">
                    <p>
                        <strong className="text-stone-900 dark:text-stone-100 font-semibold">Style:</strong> {visualAnalysis?.style}
                    </p>
                    <p>
                        <strong className="text-stone-900 dark:text-stone-100 font-semibold">Composition:</strong> {visualAnalysis?.composition}
                    </p>
                </div>
            </div>

            {/* ========================================================= */}
            {/* 4. HISTORICAL & CULTURAL CONTEXT & SYMBOLISM              */}
            {/* ========================================================= */}
            <div className="p-6 rounded-2xl border border-stone-200/90 dark:border-stone-800 bg-white dark:bg-stone-900 shadow-xs space-y-4">
                <div className="flex items-center gap-2 text-amber-700 dark:text-amber-400 text-xs uppercase tracking-widest font-semibold">
                    <BookOpen className="w-4 h-4 text-amber-600" />
                    <span>Historical & Cultural Context</span>
                </div>

                <p className="text-sm font-serif leading-relaxed text-stone-700 dark:text-stone-300">
                    {context?.historical_context}
                </p>

                {context?.symbolism && (
                    <div className="border-t border-stone-100 dark:border-stone-800 pt-3 space-y-1">
                        <span className="text-[11px] uppercase tracking-wider font-semibold text-stone-500 dark:text-stone-400">
                            Symbolism:
                        </span>
                        <p className="text-xs sm:text-sm font-serif text-stone-700 dark:text-stone-300 leading-relaxed">
                            {context?.symbolism}
                        </p>
                    </div>
                )}
            </div>

            {/* ========================================================= */}
            {/* 5. GUIDE PERSONA SELECTOR: ONLY SHOWN FOR STANDALONE ART  */}
            {/* (HIDDEN ENTIRELY WHEN VIEWING AN AUTHOR/ARTIST)           */}
            {/* ========================================================= */}
            {!artistProfile && (
                <div className="p-6 rounded-2xl border border-amber-300/80 dark:border-amber-900/60 bg-gradient-to-br from-amber-50/70 via-white to-amber-50/30 dark:from-stone-900 dark:via-stone-900 dark:to-amber-950/20 shadow-sm space-y-4">

                    <div className="flex items-center justify-between flex-wrap gap-2">
                        <div className="flex items-center gap-2 text-xs uppercase tracking-widest font-semibold text-amber-800 dark:text-amber-300">
                            <activeGuideObj.icon className="w-4 h-4 text-amber-600" />
                            <span>Select Guide Persona for This Piece</span>
                        </div>
                        <span className="text-[11px] text-stone-500 dark:text-stone-400 italic font-serif">
                            1–2 Line Unique Take
                        </span>
                    </div>

                    {/* Persona Selectors */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                        {GUIDE_OPTIONS.map((g) => {
                            const Icon = g.icon;
                            const isSelected = selectedGuide === g.id;

                            return (
                                <button
                                    key={g.id}
                                    type="button"
                                    onClick={() => onSelectGuide(g.id)}
                                    className={`p-2.5 rounded-xl border text-left transition-all duration-300 cursor-pointer flex flex-col gap-1 ${isSelected
                                            ? 'border-amber-600 bg-amber-600 text-white shadow-md scale-102 ring-1 ring-amber-600'
                                            : 'border-stone-200 dark:border-stone-800 bg-white dark:bg-stone-800/80 text-stone-700 dark:text-stone-300 hover:border-amber-400'
                                        }`}
                                >
                                    <div className="flex items-center gap-1.5">
                                        <Icon className="w-3.5 h-3.5" />
                                        <span className="text-xs font-semibold">{g.title}</span>
                                    </div>
                                    <span className={`text-[10px] ${isSelected ? 'text-amber-100' : 'text-stone-400'}`}>
                                        {g.tag}
                                    </span>
                                </button>
                            );
                        })}
                    </div>

                    {/* Distinct 1-2 Line Persona Statement Card */}
                    <div className="p-4 rounded-xl border border-amber-200/90 dark:border-amber-900/40 bg-white/90 dark:bg-stone-950/60 relative">
                        <Quote className="w-5 h-5 text-amber-600/30 absolute top-3 left-3 rotate-180" />
                        <div className="pl-6 space-y-1">
                            <span className="text-[10px] uppercase tracking-wider font-bold text-amber-700 dark:text-amber-400 block">
                                {activeGuideObj.title}’s Perspective
                            </span>
                            <p className="font-serif text-xs sm:text-sm text-stone-800 dark:text-stone-100 italic leading-relaxed">
                                “{currentPersonaText}”
                            </p>
                        </div>
                    </div>

                </div>
            )}

        </div>
    );
}
import React from 'react';
import { GraduationCap, Sparkles, Smile, Eye, Check } from 'lucide-react';

const GUIDES = [
    {
        id: 'professor',
        title: 'Professor',
        icon: GraduationCap,
        badge: 'Scholarly & Deep',
        desc: 'Formal critique, brushwork dissection, and art history lineage.'
    },
    {
        id: 'storyteller',
        title: 'Storyteller',
        icon: Sparkles,
        badge: 'Immersive Tale',
        desc: 'Cinematic prose stepping directly inside the emotions of the scene.'
    },
    {
        id: 'friendly',
        title: 'Friendly Guide',
        icon: Smile,
        badge: 'Casual & Fun',
        desc: 'Snackable curiosities and playful, bite-sized observation facts.'
    },
    {
        id: 'accessibility',
        title: 'Accessibility Guide',
        icon: Eye,
        badge: 'Spatial Clarity',
        desc: 'Rich directional layout, vivid tactile descriptions, and high contrast.'
    }
];

export default function GuideSelector({ selectedGuide, onSelectGuide }) {
    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <h3 className="text-xs uppercase tracking-widest font-semibold text-stone-500 dark:text-stone-400">
                    Choose Your AI Guide Persona
                </h3>
                <span className="text-[11px] text-amber-600 dark:text-amber-400 font-medium">
                    Adapts narrative tone & explanations
                </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {GUIDES.map((g) => {
                    const Icon = g.icon;
                    const isSelected = selectedGuide === g.id;

                    return (
                        <button
                            key={g.id}
                            type="button"
                            onClick={() => onSelectGuide(g.id)}
                            className={`group text-left p-4 rounded-2xl border transition-all duration-300 transform select-none relative flex flex-col justify-between overflow-hidden cursor-pointer ${isSelected
                                    ? 'border-amber-600 bg-amber-50/70 dark:bg-amber-950/40 text-amber-950 dark:text-amber-100 shadow-md ring-2 ring-amber-600 scale-[1.02]'
                                    : 'border-stone-200 dark:border-stone-800 bg-white dark:bg-stone-900 hover:border-amber-400/80 hover:bg-stone-50/80 dark:hover:bg-stone-800/80 hover:-translate-y-1 hover:shadow-lg text-stone-700 dark:text-stone-300'
                                } active:scale-95`}
                        >
                            {isSelected && (
                                <div className="absolute top-0 right-0 w-24 h-24 bg-amber-400/10 rounded-full blur-xl pointer-events-none" />
                            )}

                            <div>
                                <div className="flex items-center justify-between mb-3">
                                    <div className={`p-2.5 rounded-xl transition-all duration-300 ${isSelected
                                            ? 'bg-amber-600 text-white shadow-sm scale-110'
                                            : 'bg-stone-100 dark:bg-stone-800 text-stone-600 dark:text-stone-300 group-hover:bg-amber-100 dark:group-hover:bg-stone-700 group-hover:text-amber-700'
                                        }`}>
                                        <Icon className="w-5 h-5" />
                                    </div>

                                    {isSelected ? (
                                        <span className="flex items-center gap-1 text-[10px] uppercase font-bold tracking-wider text-amber-700 dark:text-amber-300 bg-amber-100/90 dark:bg-amber-900/60 px-2 py-0.5 rounded-full border border-amber-300 dark:border-amber-800">
                                            <Check className="w-3 h-3" /> Active
                                        </span>
                                    ) : (
                                        <span className="text-[10px] text-stone-400 group-hover:text-amber-600 dark:group-hover:text-amber-400 transition-colors uppercase font-medium tracking-wider">
                                            Select
                                        </span>
                                    )}
                                </div>

                                <div className="space-y-1">
                                    <h4 className="font-serif text-base font-semibold text-stone-900 dark:text-stone-100">
                                        {g.title}
                                    </h4>
                                    <p className="text-[11px] font-sans font-medium text-amber-700 dark:text-amber-400">
                                        {g.badge}
                                    </p>
                                </div>
                            </div>

                            <p className="text-xs text-stone-500 dark:text-stone-400 mt-3 leading-relaxed">
                                {g.desc}
                            </p>
                        </button>
                    );
                })}
            </div>
        </div>
    );
}
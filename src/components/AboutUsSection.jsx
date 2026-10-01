import React from 'react';
import {
    Sparkles,
    Compass,
    Headphones,
    MessageCircle,
    ArrowRight,
    HeartHandshake,
    Flame,
    BookOpen,
    Eye
} from 'lucide-react';

const PILLARS = [
    {
        icon: Compass,
        title: "Deep Vision Decoding",
        tagline: "Beyond the canvas surface",
        badge: "Multi-Agent Vision",
        description: "Traditional gallery plaques give you a date and an artist name. KalaKatha breaks down brushstroke intensity, hidden symbolic motifs, historical subtext, and composition geometry in seconds."
    },
    {
        icon: Sparkles,
        title: "Adaptive Guide Personas",
        tagline: "Art spoken in your language",
        badge: "Personalized Tone",
        description: "Whether you want a scholarly deep-dive from a Renaissance professor, an evocative bedtime story, a fun kid-friendly trivia session, or high-contrast audio descriptions, the AI reshapes itself to how you absorb culture."
    },
    {
        icon: Headphones,
        title: "Immersive Audio Journeys",
        tagline: "Listen while you gaze",
        badge: "Gemini TTS Synchronized",
        description: "Each masterpiece is structured into chronological story chapters with synchronized voice narration and visual zoom anchors, transforming static paintings into living cinema."
    },
    {
        icon: MessageCircle,
        title: "Real-Time Inquiries",
        tagline: "Have a conversation with history",
        badge: "Conversational RAG",
        description: "Curious why Mona Lisa has no eyebrows or what pigment was used in Starry Night? Ask any spontaneous question directly and receive instant historical answers."
    }
];

const USER_BENEFITS = [
    {
        icon: Flame,
        title: "Curious Art Lovers",
        badge: "Effortless Discovery",
        desc: "Explore cultural masterworks at your own leisure without intimidating academic jargon or expensive private museum tours.",
        highlight: "Unlock 500+ years of brushwork secrets with one tap."
    },
    {
        icon: BookOpen,
        title: "Students & Educators",
        badge: "Interactive Pedagogy",
        desc: "Interactive quizzes, composition breakdowns, and era-specific lineages make art history captivating, intuitive, and unforgettable.",
        highlight: "Gamified observation challenges and curated study points."
    },
    {
        icon: Eye,
        title: "Accessible to Everyone",
        badge: "Full Inclusivity",
        desc: "Screen-reader optimized descriptions, spatial audio journeys, and high-contrast color typography ensure art belongs to all human beings.",
        highlight: "Zero barriers: high contrast, audio-first topography."
    }
];

export default function AboutUsSection() {
    return (
        <section className="py-16 border-t border-stone-200 dark:border-stone-800/80 space-y-16 animate-fade-in select-none">

            {/* 1. Header & Vision Statement */}
            <div className="text-center max-w-3xl mx-auto space-y-4 px-4">
                <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-800 dark:text-amber-300 text-xs font-medium tracking-widest uppercase shadow-sm">
                    <HeartHandshake className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" />
                    <span>Our Purpose & Philosophy</span>
                </div>

                <h2 className="text-3xl sm:text-5xl font-serif text-stone-900 dark:text-stone-100 font-medium tracking-tight">
                    Democratizing the Soul of Art
                </h2>

                <p className="text-sm sm:text-base font-serif italic text-stone-600 dark:text-stone-300 leading-relaxed">
                    “Museum walls should never be a gatekeeper to wonder. KalaKatha AI bridges human emotion, centuries of heritage, and intelligent multi-agent vision to bring masterpieces directly into your hands.”
                </p>
            </div>

            {/* 2. Interactive Feature Pillars (No Forced Active State) */}
            <div className="max-w-6xl mx-auto px-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                    {PILLARS.map((pillar, idx) => {
                        const Icon = pillar.icon;

                        return (
                            <div
                                key={idx}
                                className="group relative p-6 rounded-3xl border border-stone-200/90 dark:border-stone-800 bg-white/80 dark:bg-stone-900/60 transition-all duration-500 ease-[cubic-bezier(0.34,1.56,0.64,1)] hover:-translate-y-2 hover:scale-[1.02] hover:shadow-xl hover:border-amber-400/80 dark:hover:border-amber-500/60 hover:bg-amber-50/40 dark:hover:bg-amber-950/20 flex flex-col justify-between overflow-hidden cursor-default active:scale-98"
                            >
                                {/* Soft glow wash on hover */}
                                <div className="absolute top-0 right-0 w-32 h-32 bg-amber-400/10 rounded-full blur-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />

                                <div className="space-y-4 relative z-10">
                                    <div className="flex items-center justify-between">
                                        <div className="w-12 h-12 rounded-2xl bg-stone-100 dark:bg-stone-800 text-stone-700 dark:text-stone-300 group-hover:bg-amber-600 group-hover:text-white group-hover:shadow-lg group-hover:scale-105 flex items-center justify-center transition-all duration-500">
                                            <Icon className="w-6 h-6" />
                                        </div>

                                        <span className="text-[10px] uppercase tracking-wider text-stone-400 group-hover:text-amber-700 dark:group-hover:text-amber-300 font-medium transition-colors">
                                            {pillar.badge}
                                        </span>
                                    </div>

                                    <div>
                                        <span className="text-[10px] uppercase tracking-wider text-amber-700 dark:text-amber-400 font-semibold block">
                                            {pillar.tagline}
                                        </span>
                                        <h3 className="font-serif text-lg font-bold text-stone-900 dark:text-stone-100 mt-0.5">
                                            {pillar.title}
                                        </h3>
                                    </div>

                                    <p className="text-xs text-stone-600 dark:text-stone-300 leading-relaxed font-sans">
                                        {pillar.description}
                                    </p>
                                </div>

                                <div className="pt-4 border-t border-stone-100 dark:border-stone-800/80 mt-4 flex items-center justify-between text-[11px] font-medium text-stone-400 group-hover:text-amber-700 dark:group-hover:text-amber-400 transition-colors relative z-10">
                                    <span>Explore capability</span>
                                    <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1.5 transition-transform duration-300" />
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* 3. Who KalaKatha Helps (Clean Responsive Hover Cards) */}
            <div className="max-w-5xl mx-auto px-4">
                <div className="rounded-3xl border border-stone-200/90 dark:border-stone-800 bg-stone-100/50 dark:bg-stone-900/50 p-6 sm:p-10 shadow-sm backdrop-blur-md space-y-8">

                    <div className="text-center space-y-1.5">
                        <span className="text-xs uppercase tracking-widest text-amber-600 dark:text-amber-400 font-semibold">
                            Empowering Humanity
                        </span>
                        <h3 className="font-serif text-2xl sm:text-4xl font-medium text-stone-900 dark:text-stone-100 tracking-tight">
                            How KalaKatha Enriches Your Experience
                        </h3>
                        <p className="text-xs text-stone-500 dark:text-stone-400">
                            Thoughtfully architected to make art engaging, educational, and accessible
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                        {USER_BENEFITS.map((b, i) => {
                            const BenefitIcon = b.icon;

                            return (
                                <div
                                    key={i}
                                    className="group relative p-6 rounded-2xl border border-stone-200/90 dark:border-stone-700/80 bg-white/80 dark:bg-stone-800/60 transition-all duration-500 ease-[cubic-bezier(0.34,1.56,0.64,1)] hover:-translate-y-2 hover:scale-[1.02] hover:shadow-xl hover:border-amber-400/80 dark:hover:border-amber-500/60 flex flex-col justify-between overflow-hidden cursor-default active:scale-98"
                                >
                                    <div className="space-y-3">
                                        <div className="flex items-center justify-between">
                                            <div className="w-9 h-9 rounded-xl flex items-center justify-center font-bold text-xs bg-amber-100 dark:bg-amber-950/70 text-amber-800 dark:text-amber-300 group-hover:bg-amber-600 group-hover:text-white transition-colors duration-300">
                                                0{i + 1}
                                            </div>

                                            <span className="text-[10px] font-medium uppercase tracking-wider px-2 py-0.5 rounded-full text-stone-400 group-hover:text-amber-700 dark:group-hover:text-amber-300 transition-colors">
                                                {b.badge}
                                            </span>
                                        </div>

                                        <div className="flex items-center gap-2">
                                            <BenefitIcon className="w-4 h-4 text-stone-400 group-hover:text-amber-600 dark:group-hover:text-amber-400 transition-colors" />
                                            <h4 className="font-serif text-lg font-semibold text-stone-900 dark:text-stone-100">
                                                {b.title}
                                            </h4>
                                        </div>

                                        <p className="text-xs text-stone-600 dark:text-stone-300 leading-relaxed font-sans">
                                            {b.desc}
                                        </p>
                                    </div>

                                    <div className="mt-5 pt-3 border-t border-stone-100 dark:border-stone-700/50 text-[11px] font-serif text-stone-400 group-hover:text-amber-700 dark:group-hover:text-amber-400 font-medium transition-colors">
                                        {b.highlight}
                                    </div>
                                </div>
                            );
                        })}
                    </div>

                </div>
            </div>

            {/* 4. Editorial Museum Footer Note */}
            <div className="text-center pt-8 border-t border-stone-200/60 dark:border-stone-800/60 max-w-xl mx-auto space-y-2">
                <p className="font-serif text-sm text-stone-700 dark:text-stone-300">
                    KalaKatha AI • Cultivating Heritage Through Intelligent Vision
                </p>
                <p className="text-[11px] text-stone-400 dark:text-stone-500 font-sans tracking-wide">
                    Designed with Google Arts & Culture elegance • Accessible to all
                </p>
            </div>

        </section>
    );
}
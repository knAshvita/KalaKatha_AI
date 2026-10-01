import React, { useState, useRef, useEffect } from 'react';
import { Play, Pause, Loader2, AlertCircle, Volume2, Sparkles, Clock } from 'lucide-react';
import { getStoryAudio } from '../api/kalakathaApi';

export default function ListenTab({ story, sessionId, onFocusChapter }) {
    const [activeChapterIndex, setActiveChapterIndex] = useState(0);
    const [isPlaying, setIsPlaying] = useState(false);
    const [loadingAudio, setLoadingAudio] = useState(false);
    const [audioError, setAudioError] = useState(null);
    const [cachedAudio, setCachedAudio] = useState({});
    const [activeVoice, setActiveVoice] = useState('Puck');
    const [audioProgress, setAudioProgress] = useState(0);

    const audioRef = useRef(null);

    // Normalize chapters array
    const rawChapters = story?.chapters || [];
    const chapters = rawChapters.map((chap, idx) => ({
        id: chap.chapter_id || chap.id || `chapter_${idx + 1}`,
        title: chap.title || `Chapter ${idx + 1}`,
        text: chap.narration || chap.text || '',
        focus: chap.focus_region || chap.focus || 'center',
        duration: chap.estimated_duration_seconds || 30
    }));

    const currentChapter = chapters[activeChapterIndex] || chapters[0];
    const storyTitle = story?.story_title || story?.title || "Exhibition Audio Guide";
    const openingText = story?.opening || "Step inside the emotional and historical currents of this masterpiece.";

    // Stop audio on unmount or tab switch
    useEffect(() => {
        return () => {
            if (audioRef.current) {
                audioRef.current.pause();
            }
        };
    }, []);

    const handleSelectChapter = (index) => {
        if (index === activeChapterIndex) return;
        setActiveChapterIndex(index);
        if (audioRef.current) {
            audioRef.current.pause();
        }
        setIsPlaying(false);
        setAudioError(null);
        setAudioProgress(0);

        const targetFocus = chapters[index]?.focus;
        if (onFocusChapter && targetFocus) {
            onFocusChapter(targetFocus);
        }
    };

    const handlePlayNarrative = async () => {
        if (!currentChapter) return;

        // Toggle pause if already playing
        if (isPlaying && audioRef.current) {
            audioRef.current.pause();
            setIsPlaying(false);
            return;
        }

        // If audio is already loaded and paused, resume playback
        if (audioRef.current && audioRef.current.src && audioRef.current.src.includes(currentChapter.id) && audioRef.current.paused) {
            try {
                await audioRef.current.play();
                setIsPlaying(true);
                return;
            } catch (err) {
                console.warn("Resume failed, regenerating audio:", err);
            }
        }

        // Check local cache for previously generated audio
        const cachedUrl = cachedAudio[currentChapter.id];
        if (cachedUrl && audioRef.current) {
            try {
                audioRef.current.src = cachedUrl;
                await audioRef.current.play();
                setIsPlaying(true);
                return;
            } catch (err) {
                console.warn("Cached audio playback failed, re-fetching:", err);
            }
        }

        // Fetch fresh audio from real backend Gemini TTS
        try {
            setLoadingAudio(true);
            setAudioError(null);

            if (!sessionId) {
                throw new Error("Session ID is required to synthesize story audio.");
            }

            const response = await getStoryAudio(sessionId, currentChapter.id);
            const audioUrl = response.audio_url || response.audio;

            if (!audioUrl) {
                throw new Error("No audio payload returned from backend TTS.");
            }

            if (response.voice) {
                setActiveVoice(response.voice);
            }

            // Cache URL for this session
            setCachedAudio((prev) => ({ ...prev, [currentChapter.id]: audioUrl }));

            if (audioRef.current) {
                audioRef.current.src = audioUrl;
                await audioRef.current.play();
                setIsPlaying(true);
            }
        } catch (err) {
            setAudioError(err.message || 'Failed to generate Gemini TTS audio.');
        } finally {
            setLoadingAudio(false);
        }
    };

    const handleTimeUpdate = () => {
        if (audioRef.current && audioRef.current.duration) {
            const current = audioRef.current.currentTime;
            const total = audioRef.current.duration;
            setAudioProgress((current / total) * 100);
        }
    };

    return (
        <div className="space-y-6 animate-fade-in">
            <audio
                ref={audioRef}
                onEnded={() => {
                    setIsPlaying(false);
                    setAudioProgress(100);
                }}
                onTimeUpdate={handleTimeUpdate}
                onError={() => {
                    setIsPlaying(false);
                    setAudioError("Audio playback error. Please try generating again.");
                }}
                className="hidden"
            />

            {/* Header info */}
            <div className="space-y-2">
                <div className="flex items-center justify-between">
                    <span className="text-[10px] uppercase tracking-widest font-bold text-amber-700 dark:text-amber-400 bg-amber-100 dark:bg-amber-950/70 px-2.5 py-0.5 rounded-full border border-amber-300 dark:border-amber-800 flex items-center gap-1.5">
                        <Sparkles className="w-3 h-3 text-amber-600" />
                        <span>Curated Audio Guide</span>
                    </span>
                    <span className="text-xs text-stone-500 dark:text-stone-400 flex items-center gap-1">
                        <Volume2 className="w-3.5 h-3.5 text-amber-600" />
                        <span>Gemini Voice: <strong>{activeVoice}</strong></span>
                    </span>
                </div>

                <h3 className="font-serif text-2xl text-stone-900 dark:text-stone-100 font-bold">{storyTitle}</h3>
                <p className="text-sm italic font-serif text-stone-600 dark:text-stone-300 leading-relaxed">
                    “{openingText}”
                </p>
            </div>

            {/* Chapter Selection Ribbon */}
            <div className="flex gap-2 border-b border-stone-200 dark:border-stone-800 pb-3 overflow-x-auto no-scrollbar">
                {chapters.map((chap, idx) => (
                    <button
                        key={chap.id || idx}
                        type="button"
                        onClick={() => handleSelectChapter(idx)}
                        className={`px-3.5 py-2 rounded-xl text-xs uppercase tracking-wider font-semibold whitespace-nowrap transition cursor-pointer ${
                            activeChapterIndex === idx
                                ? 'bg-amber-600 text-white shadow-md'
                                : 'bg-stone-100 dark:bg-stone-800/90 text-stone-600 dark:text-stone-300 hover:bg-stone-200 dark:hover:bg-stone-700'
                        }`}
                    >
                        Ch. {idx + 1}: {chap.title}
                    </button>
                ))}
            </div>

            {/* Active Chapter Card */}
            {currentChapter && (
                <div className="p-6 rounded-3xl border border-stone-200/90 dark:border-stone-800 bg-white dark:bg-stone-900 space-y-6 shadow-sm">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                        <div>
                            <span className="text-xs uppercase tracking-widest text-amber-700 dark:text-amber-400 font-bold">
                                Chapter {activeChapterIndex + 1} of {chapters.length}
                            </span>
                            <h4 className="font-serif text-xl sm:text-2xl font-bold text-stone-900 dark:text-stone-100 mt-0.5">
                                {currentChapter.title}
                            </h4>
                            <div className="flex items-center gap-3 text-xs text-stone-500 dark:text-stone-400 mt-1">
                                <span className="flex items-center gap-1">
                                    <Clock className="w-3.5 h-3.5 text-amber-600" />
                                    <span>~{currentChapter.duration}s Narration</span>
                                </span>
                                <span>•</span>
                                <span>Focus: <strong className="capitalize">{currentChapter.focus}</strong></span>
                            </div>
                        </div>

                        {/* Listen Button */}
                        <button
                            type="button"
                            onClick={handlePlayNarrative}
                            disabled={loadingAudio}
                            className="flex items-center justify-center gap-2.5 px-6 py-3 rounded-full bg-amber-600 hover:bg-amber-700 active:scale-95 text-white font-medium text-xs tracking-wider uppercase transition shadow-md disabled:opacity-50 cursor-pointer flex-shrink-0"
                        >
                            {loadingAudio ? (
                                <Loader2 className="w-4 h-4 animate-spin" />
                            ) : isPlaying ? (
                                <Pause className="w-4 h-4" />
                            ) : (
                                <Play className="w-4 h-4 fill-white" />
                            )}
                            <span>{loadingAudio ? 'Synthesizing...' : isPlaying ? 'Pause Audio' : 'Listen with Gemini TTS'}</span>
                        </button>
                    </div>

                    {/* Visual Progress Bar when playing */}
                    {audioProgress > 0 && (
                        <div className="w-full bg-stone-100 dark:bg-stone-800 h-1.5 rounded-full overflow-hidden">
                            <div
                                className="bg-amber-600 h-full transition-all duration-200"
                                style={{ width: `${audioProgress}%` }}
                            />
                        </div>
                    )}

                    {/* Chapter Narration Prose */}
                    <div className="pt-2 border-t border-stone-100 dark:border-stone-800">
                        <p className="text-base sm:text-lg font-serif leading-relaxed text-stone-800 dark:text-stone-200 selection:bg-amber-400 selection:text-black">
                            {currentChapter.text}
                        </p>
                    </div>

                    {audioError && (
                        <div className="flex items-center gap-2 text-xs text-rose-700 bg-rose-50 dark:bg-rose-950/40 p-3.5 rounded-xl border border-rose-200 dark:border-rose-900">
                            <AlertCircle className="w-4 h-4 flex-shrink-0 text-rose-600" />
                            <span>{audioError}</span>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
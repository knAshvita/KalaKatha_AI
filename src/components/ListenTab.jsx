import React, { useState, useRef } from 'react';
import { Play, Pause, Loader2, AlertCircle } from 'lucide-react';
import { getNarration } from '../api/kalakathaApi';

export default function ListenTab({ story, artworkId, onFocusChapter, isMock }) {
    const [activeChapterIndex, setActiveChapterIndex] = useState(0);
    const [isPlaying, setIsPlaying] = useState(false);
    const [loadingAudio, setLoadingAudio] = useState(false);
    const [audioError, setAudioError] = useState(null);
    const audioRef = useRef(null);

    const chapters = story?.chapters || [];
    const currentChapter = chapters[activeChapterIndex];

    const handleSelectChapter = (index) => {
        setActiveChapterIndex(index);
        if (audioRef.current) {
            audioRef.current.pause();
        }
        setIsPlaying(false);
        setAudioError(null);
        if (onFocusChapter) {
            onFocusChapter(chapters[index]?.focus);
        }
    };

    const handlePlayNarrative = async () => {
        if (isPlaying && audioRef.current) {
            audioRef.current.pause();
            setIsPlaying(false);
            return;
        }

        try {
            setLoadingAudio(true);
            setAudioError(null);

            if (isMock) {
                const synth = window.speechSynthesis;
                if (synth) {
                    synth.cancel();
                    const utterance = new SpeechSynthesisUtterance(currentChapter?.text || story?.opening);
                    utterance.onend = () => setIsPlaying(false);
                    synth.speak(utterance);
                    setIsPlaying(true);
                    setLoadingAudio(false);
                    return;
                }
            }

            const response = await getNarration(artworkId, currentChapter?.id || 'chapter_1');
            const audioUrl = response.audio_url || response.audio;
            if (!audioUrl) throw new Error("No audio payload returned from backend TTS.");

            if (audioRef.current) {
                audioRef.current.src = audioUrl;
                await audioRef.current.play();
                setIsPlaying(true);
            }
        } catch (err) {
            setAudioError(err.message || 'Failed to play Gemini TTS narration.');
        } finally {
            setLoadingAudio(false);
        }
    };

    return (
        <div className="space-y-6 animate-fade-in">
            <audio ref={audioRef} onEnded={() => setIsPlaying(false)} className="hidden" />

            <div className="space-y-2">
                <h3 className="font-serif text-2xl text-stone-900 dark:text-stone-100">{story?.title || "Artwork Story"}</h3>
                <p className="text-sm italic font-serif text-stone-600 dark:text-stone-300 leading-relaxed">
                    "{story?.opening}"
                </p>
            </div>

            <div className="flex gap-2 border-b border-stone-200 dark:border-stone-800 pb-3 overflow-x-auto">
                {chapters.map((chap, idx) => (
                    <button
                        key={chap.id || idx}
                        onClick={() => handleSelectChapter(idx)}
                        className={`px-4 py-2 rounded-lg text-xs uppercase tracking-wider font-medium whitespace-nowrap transition ${activeChapterIndex === idx
                                ? 'bg-stone-900 dark:bg-stone-100 text-white dark:text-stone-900'
                                : 'bg-stone-100 dark:bg-stone-800 text-stone-600 dark:text-stone-400 hover:bg-stone-200 dark:hover:bg-stone-700'
                            }`}
                    >
                        Chapter {idx + 1}: {chap.title}
                    </button>
                ))}
            </div>

            {currentChapter && (
                <div className="p-6 rounded-2xl border border-stone-200 dark:border-stone-800 bg-white dark:bg-stone-900 space-y-6 shadow-sm">
                    <div className="flex items-center justify-between">
                        <div>
                            <span className="text-xs uppercase tracking-widest text-amber-700 dark:text-amber-400 font-semibold">
                                Chapter {activeChapterIndex + 1}
                            </span>
                            <h4 className="font-serif text-xl font-medium text-stone-900 dark:text-stone-100">{currentChapter.title}</h4>
                        </div>

                        <button
                            onClick={handlePlayNarrative}
                            disabled={loadingAudio}
                            className="flex items-center gap-2 px-5 py-2.5 rounded-full bg-amber-600 hover:bg-amber-700 text-white font-medium text-xs tracking-wider uppercase transition shadow-md disabled:opacity-50"
                        >
                            {loadingAudio ? (
                                <Loader2 className="w-4 h-4 animate-spin" />
                            ) : isPlaying ? (
                                <Pause className="w-4 h-4" />
                            ) : (
                                <Play className="w-4 h-4" />
                            )}
                            <span>{isPlaying ? 'Pause Narration' : 'Listen with Gemini TTS'}</span>
                        </button>
                    </div>

                    <p className="text-base font-serif leading-relaxed text-stone-800 dark:text-stone-200">
                        {currentChapter.text}
                    </p>

                    {audioError && (
                        <div className="flex items-center gap-2 text-xs text-rose-600 bg-rose-50 dark:bg-rose-950/40 p-3 rounded-lg border border-rose-200 dark:border-rose-900">
                            <AlertCircle className="w-4 h-4 flex-shrink-0" />
                            <span>{audioError}</span>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
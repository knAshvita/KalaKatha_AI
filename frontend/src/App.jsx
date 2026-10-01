import React, { useState } from 'react';
import Navbar from './components/Navbar';
import HeroGallery from './components/HeroGallery';
import ArtworkViewer from './components/ArtworkViewer';
import LoadingOverlay from './components/LoadingOverlay';
import ExploreTab from './components/ExploreTab';
import ListenTab from './components/ListenTab';
import AskTab from './components/AskTab';
import LearnTab from './components/LearnTab';
import CinematicIntro from './components/CinematicIntro';
import { analyzeArtwork } from './api/kalakathaApi';
import {
    Compass,
    Headphones,
    MessageCircle,
    Lightbulb,
    AlertTriangle,
    RotateCcw,
    Layers,
    Sparkles
} from 'lucide-react';

export default function App() {
    const [darkMode, setDarkMode] = useState(false);
    const [highContrast, setHighContrast] = useState(false);
    const [introFinished, setIntroFinished] = useState(false);

    // Guide Persona selection state
    const [selectedGuide, setSelectedGuide] = useState('storyteller');
    const [activeFocus, setActiveFocus] = useState(null);

    // Interactive stage active tab: 'explore' | 'story' | 'ask' | 'learn'
    const [activeTab, setActiveTab] = useState('explore');

    // Artwork & Session state
    const [currentArtworkImage, setCurrentArtworkImage] = useState(null);
    const [sessionId, setSessionId] = useState(null);
    const [analysisData, setAnalysisData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [errorMessage, setErrorMessage] = useState(null);

    const processArtwork = async (imageInput, title = 'Selected Artwork') => {
        // Set visual preview
        if (typeof imageInput === 'string') {
            setCurrentArtworkImage(imageInput);
        } else if (imageInput instanceof File || imageInput instanceof Blob) {
            const previewUrl = URL.createObjectURL(imageInput);
            setCurrentArtworkImage(previewUrl);
        }

        setLoading(true);
        setErrorMessage(null);
        setActiveFocus(null);
        setActiveTab('explore');

        try {
            // Real live backend call: POST /api/analyze (multipart/form-data)
            const result = await analyzeArtwork(imageInput, selectedGuide, title);
            setAnalysisData(result);
            setSessionId(result.session_id);
        } catch (err) {
            console.error("KalaKatha backend analysis error:", err);
            setErrorMessage(err.message || 'Analysis failed. Please check the backend connection.');
            setAnalysisData(null);
            setSessionId(null);
        } finally {
            setLoading(false);
        }
    };

    const handleReset = () => {
        setAnalysisData(null);
        setSessionId(null);
        setCurrentArtworkImage(null);
        setActiveFocus(null);
        setErrorMessage(null);
        setActiveTab('explore');
    };

    // Extract unified experience data
    const exp = analysisData?.experience;
    const visual = exp?.visual_analysis || analysisData?.visual_analysis;
    const context = exp?.context || analysisData?.context;
    const accessibility = exp?.accessibility || analysisData?.accessibility;
    const story = exp?.story || analysisData?.immersive_story;
    const learning = exp?.learning || analysisData?.learning_content;
    const explore = exp?.explore;
    const regions = explore?.regions || [];

    const artworkTitle = exp?.artwork?.title || visual?.artwork_title || 'Exhibition Artwork';
    const artworkArtist = exp?.artwork?.artist || visual?.artist;
    const artworkPeriod = exp?.artwork?.period || visual?.period;

    return (
        <div className={`${darkMode ? 'dark' : ''} ${highContrast ? 'contrast-125' : ''}`}>
            {/* 3D Collision Landing Intro */}
            {!introFinished && (
                <CinematicIntro onComplete={() => setIntroFinished(true)} />
            )}

            <div className="min-h-screen bg-museum-bg dark:bg-museum-darkBg text-stone-900 dark:text-stone-100 transition-colors font-sans selection:bg-amber-500 selection:text-white">
                <Navbar
                    darkMode={darkMode}
                    setDarkMode={setDarkMode}
                    highContrast={highContrast}
                    setHighContrast={setHighContrast}
                    onReset={handleReset}
                    hasArtwork={!!analysisData || !!currentArtworkImage}
                />

                <main className="max-w-7xl mx-auto px-4 sm:px-6 py-6">
                    {/* Error Notification Banner */}
                    {errorMessage && (
                        <div className="mb-6 p-4 rounded-2xl border border-rose-200 dark:border-rose-900 bg-rose-50 dark:bg-rose-950/40 text-rose-800 dark:text-rose-200 flex items-center justify-between shadow-sm animate-fade-in">
                            <div className="flex items-center gap-3">
                                <AlertTriangle className="w-5 h-5 flex-shrink-0 text-rose-600" />
                                <div>
                                    <p className="text-xs md:text-sm font-semibold">Artwork Analysis Notice</p>
                                    <p className="text-xs opacity-90">{errorMessage}</p>
                                </div>
                            </div>
                            <button
                                onClick={handleReset}
                                className="text-xs uppercase tracking-wider font-semibold underline hover:opacity-80 cursor-pointer ml-4"
                            >
                                Try Again
                            </button>
                        </div>
                    )}

                    {/* Loading State Overlay */}
                    {loading && <LoadingOverlay />}

                    {/* Exhibition & Gallery Landing View (When no artwork analyzed) */}
                    {!loading && !analysisData && (
                        <HeroGallery
                            onSelectPreloaded={(art) => processArtwork(art.image, art.title)}
                            onUploadImage={(dataUrl, name) => processArtwork(dataUrl, name)}
                            selectedGuide={selectedGuide}
                            onSelectGuide={setSelectedGuide}
                        />
                    )}

                    {/* Museum Interactive Stage: Multi-Tab Experience */}
                    {!loading && analysisData && (
                        <div className="space-y-6 animate-fade-in">

                            {/* Top Stage Bar: Session & Metadata */}
                            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-3xl bg-white/70 dark:bg-stone-900/60 border border-stone-200/80 dark:border-stone-800 backdrop-blur-md shadow-xs">
                                <div className="flex items-center gap-3">
                                    <div className="w-3 h-3 rounded-full bg-emerald-500 animate-pulse" />
                                    <div>
                                        <div className="flex items-center gap-2">
                                            <h1 className="font-serif text-lg font-bold text-stone-900 dark:text-stone-100">
                                                {artworkTitle}
                                            </h1>
                                            {artworkArtist && (
                                                <span className="text-xs text-amber-700 dark:text-amber-400 font-sans font-semibold">
                                                    by {artworkArtist}
                                                </span>
                                            )}
                                        </div>
                                        <p className="text-[11px] text-stone-500 dark:text-stone-400 font-sans">
                                            Session: <span className="font-mono">{sessionId}</span> {artworkPeriod ? `• ${artworkPeriod}` : ''}
                                        </p>
                                    </div>
                                </div>

                                <div className="flex items-center gap-2">
                                    <span className="text-[11px] uppercase tracking-wider font-bold text-amber-700 dark:text-amber-400 bg-amber-100 dark:bg-amber-950/70 px-3 py-1 rounded-full border border-amber-300 dark:border-amber-800 capitalize">
                                        Guide: {selectedGuide}
                                    </span>
                                    <button
                                        onClick={handleReset}
                                        className="flex items-center gap-1.5 text-xs px-3 py-1 rounded-full bg-stone-100 dark:bg-stone-800 hover:bg-stone-200 dark:hover:bg-stone-700 text-stone-700 dark:text-stone-300 transition cursor-pointer"
                                        title="Analyze another artwork"
                                    >
                                        <RotateCcw className="w-3.5 h-3.5" />
                                        <span>Change</span>
                                    </button>
                                </div>
                            </div>

                            {/* Two-Column Stage Layout */}
                            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">

                                {/* Left Column (7 cols): Artwork Canvas Viewer with Hotspots & Pigments */}
                                <div className="lg:col-span-7 sticky top-24 space-y-4">
                                    <ArtworkViewer
                                        imageSrc={currentArtworkImage}
                                        title={artworkTitle}
                                        artist={artworkArtist}
                                        period={artworkPeriod}
                                        activeFocus={activeFocus}
                                        colors={visual?.colors}
                                        regions={regions}
                                    />
                                </div>

                                {/* Right Column (5 cols): Interactive Tabbed Exhibition Terminal */}
                                <div className="lg:col-span-5 space-y-5">

                                    {/* Tab Navigation Ribbon */}
                                    <div className="grid grid-cols-4 p-1.5 rounded-2xl bg-stone-200/80 dark:bg-stone-800/80 border border-stone-300/60 dark:border-stone-700/60 shadow-xs">
                                        <button
                                            type="button"
                                            onClick={() => setActiveTab('explore')}
                                            className={`flex items-center justify-center gap-1.5 py-2.5 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                                                activeTab === 'explore'
                                                    ? 'bg-white dark:bg-stone-900 text-amber-700 dark:text-amber-400 shadow-sm'
                                                    : 'text-stone-600 dark:text-stone-400 hover:text-stone-900 dark:hover:text-stone-100'
                                            }`}
                                        >
                                            <Compass className="w-3.5 h-3.5" />
                                            <span>Explore</span>
                                        </button>

                                        <button
                                            type="button"
                                            onClick={() => setActiveTab('story')}
                                            className={`flex items-center justify-center gap-1.5 py-2.5 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                                                activeTab === 'story'
                                                    ? 'bg-white dark:bg-stone-900 text-amber-700 dark:text-amber-400 shadow-sm'
                                                    : 'text-stone-600 dark:text-stone-400 hover:text-stone-900 dark:hover:text-stone-100'
                                            }`}
                                        >
                                            <Headphones className="w-3.5 h-3.5" />
                                            <span>Story</span>
                                        </button>

                                        <button
                                            type="button"
                                            onClick={() => setActiveTab('ask')}
                                            className={`flex items-center justify-center gap-1.5 py-2.5 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                                                activeTab === 'ask'
                                                    ? 'bg-white dark:bg-stone-900 text-amber-700 dark:text-amber-400 shadow-sm'
                                                    : 'text-stone-600 dark:text-stone-400 hover:text-stone-900 dark:hover:text-stone-100'
                                            }`}
                                        >
                                            <MessageCircle className="w-3.5 h-3.5" />
                                            <span>Ask</span>
                                        </button>

                                        <button
                                            type="button"
                                            onClick={() => setActiveTab('learn')}
                                            className={`flex items-center justify-center gap-1.5 py-2.5 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                                                activeTab === 'learn'
                                                    ? 'bg-white dark:bg-stone-900 text-amber-700 dark:text-amber-400 shadow-sm'
                                                    : 'text-stone-600 dark:text-stone-400 hover:text-stone-900 dark:hover:text-stone-100'
                                            }`}
                                        >
                                            <Lightbulb className="w-3.5 h-3.5" />
                                            <span>Learn</span>
                                        </button>
                                    </div>

                                    {/* Active Tab View */}
                                    <div className="min-h-[480px]">
                                        {activeTab === 'explore' && (
                                            <ExploreTab
                                                visualAnalysis={visual}
                                                context={context}
                                                accessibility={accessibility}
                                                personaNotes={analysisData?.persona_notes}
                                                selectedGuide={selectedGuide}
                                                onSelectGuide={setSelectedGuide}
                                            />
                                        )}

                                        {activeTab === 'story' && (
                                            <ListenTab
                                                story={story}
                                                sessionId={sessionId}
                                                onFocusChapter={(focus) => setActiveFocus(focus)}
                                            />
                                        )}

                                        {activeTab === 'ask' && (
                                            <AskTab
                                                sessionId={sessionId}
                                                artworkTitle={artworkTitle}
                                            />
                                        )}

                                        {activeTab === 'learn' && (
                                            <LearnTab
                                                learning={learning}
                                                sessionId={sessionId}
                                            />
                                        )}
                                    </div>

                                </div>

                            </div>

                        </div>
                    )}
                </main>
            </div>
        </div>
    );
}
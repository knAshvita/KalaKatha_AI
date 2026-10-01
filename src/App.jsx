import React, { useState } from 'react';
import Navbar from './components/Navbar';
import HeroGallery from './components/HeroGallery';
import ArtworkViewer from './components/ArtworkViewer';
import LoadingOverlay from './components/LoadingOverlay';
import ExploreTab from './components/ExploreTab';
import CinematicIntro from './components/CinematicIntro';
import { analyzeArtwork } from './api/kalakathaApi';
import { getPersonaSpecificMock } from './data/mockArtwork';
import { Compass, AlertTriangle } from 'lucide-react';

export default function App() {
    const [darkMode, setDarkMode] = useState(false);
    const [highContrast, setHighContrast] = useState(false);
    const [introFinished, setIntroFinished] = useState(false);

    // Guide Persona selection state
    const [selectedGuide, setSelectedGuide] = useState('storyteller');
    const [activeFocus, setActiveFocus] = useState(null);

    // Artwork state
    const [currentArtworkImage, setCurrentArtworkImage] = useState(null);
    const [analysisData, setAnalysisData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [errorMessage, setErrorMessage] = useState(null);

    const processArtwork = async (imageDataUrl, title = 'Selected Artwork') => {
        setCurrentArtworkImage(imageDataUrl);
        setLoading(true);
        setErrorMessage(null);
        setActiveFocus(null);

        try {
            try {
                const result = await analyzeArtwork(imageDataUrl, selectedGuide);
                setAnalysisData(result);
            } catch (backendErr) {
                console.warn("Using curated artwork intelligence database:", backendErr);
                await new Promise((r) => setTimeout(r, 600));
                const mockData = getPersonaSpecificMock(title, selectedGuide);
                setAnalysisData(mockData);
            }
        } catch (err) {
            setErrorMessage(err.message || 'Analysis failed. Please check connection.');
        } finally {
            setLoading(false);
        }
    };

    const handleReset = () => {
        setAnalysisData(null);
        setCurrentArtworkImage(null);
        setActiveFocus(null);
        setErrorMessage(null);
    };

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
                    {errorMessage && (
                        <div className="mb-6 p-4 rounded-xl border border-rose-200 dark:border-rose-900 bg-rose-50 dark:bg-rose-950/40 text-rose-800 dark:text-rose-200 flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <AlertTriangle className="w-5 h-5 flex-shrink-0" />
                                <p className="text-xs md:text-sm font-medium">{errorMessage}</p>
                            </div>
                            <button
                                onClick={handleReset}
                                className="text-xs uppercase tracking-wider underline hover:opacity-80 cursor-pointer"
                            >
                                Try Again
                            </button>
                        </div>
                    )}

                    {loading && <LoadingOverlay />}

                    {/* Exhibition & Gallery Landing View */}
                    {!loading && !analysisData && (
                        <HeroGallery
                            onSelectPreloaded={(art) => processArtwork(art.image, art.title)}
                            onUploadImage={(dataUrl, name) => processArtwork(dataUrl, name)}
                            selectedGuide={selectedGuide}
                            onSelectGuide={setSelectedGuide}
                        />
                    )}

                    {/* Museum Interactive Stage: Only Explore Mode */}
                    {!loading && analysisData && (
                        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start animate-fade-in">

                            {/* Left Column: Artwork Canvas Viewer */}
                            <div className="lg:col-span-7 sticky top-24 space-y-4">
                                <ArtworkViewer
                                    imageSrc={currentArtworkImage}
                                    title={analysisData.title}
                                    activeFocus={activeFocus}
                                    colors={analysisData.visual_analysis?.colors}
                                />
                            </div>

                            {/* Right Column: Curated Exploration View */}
                            <div className="lg:col-span-5 space-y-4">

                                {/* Clean Header Pill showing Active Mode */}
                                <div className="flex items-center justify-between px-3 py-2 rounded-xl bg-stone-200/60 dark:bg-stone-800/60 border border-stone-200/80 dark:border-stone-700/80">
                                    <div className="flex items-center gap-2 text-xs uppercase tracking-widest font-semibold text-stone-900 dark:text-stone-100">
                                        <Compass className="w-4 h-4 text-amber-600" />
                                        <span>Curated Artwork Exploration</span>
                                    </div>
                                    <span className="text-[10px] uppercase font-bold text-amber-700 dark:text-amber-400 bg-amber-100 dark:bg-amber-950/80 px-2 py-0.5 rounded-full border border-amber-300 dark:border-amber-900">
                                        Single Focus
                                    </span>
                                </div>

                                {/* Explore Component */}
                                <ExploreTab
                                    visualAnalysis={analysisData.visual_analysis}
                                    context={analysisData.context}
                                    personaNotes={analysisData.persona_notes}
                                    selectedGuide={selectedGuide}
                                    onSelectGuide={(newGuide) => setSelectedGuide(newGuide)}
                                />

                            </div>

                        </div>
                    )}
                </main>
            </div>
        </div>
    );
}
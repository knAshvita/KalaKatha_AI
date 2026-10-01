import React, { useRef, useState, useEffect } from 'react';
import { Upload, ArrowRight, Sparkles, ChevronLeft, ChevronRight, Quote, Compass } from 'lucide-react';
import { PRELOADED_ARTWORKS } from '../data/mockArtwork';
import GuideSelector from './GuideSelector';
import ArtistSpotlight from './ArtistSpotlight';
import AboutUsSection from './AboutUsSection';

const ART_QUOTES = [
    {
        quote: "Art does not reproduce what we see; rather, it makes us see.",
        author: "Paul Klee",
        context: "On unveiling hidden layers beyond the surface",
        era: "Expressionism & Bauhaus"
    },
    {
        quote: "Painting is poetry that is seen rather than felt, and poetry is painting that is felt rather than seen.",
        author: "Leonardo da Vinci",
        context: "On storytelling through brushwork",
        era: "High Renaissance"
    },
    {
        quote: "To be an artist is to believe in life. Art is to console those who are broken by life.",
        author: "Vincent van Gogh",
        context: "On the emotional resonance of color",
        era: "Post-Impressionism"
    },
    {
        quote: "Every portrait that is painted with feeling is a portrait of the artist, not of the sitter.",
        author: "Oscar Wilde",
        context: "On entering the painter's inner psyche",
        era: "Aesthetic Movement"
    },
    {
        quote: "Color is the keyboard, the eyes are the harmonies, the soul is the piano with many strings.",
        author: "Wassily Kandinsky",
        context: "On synesthetic and sensory immersion",
        era: "Abstract Expressionism"
    },
    {
        quote: "I found I could say things with color and shapes that I couldn't say any other way—things I had no words for.",
        author: "Georgia O'Keeffe",
        context: "On expressing the unspoken canvas",
        era: "American Modernism"
    }
];

export default function HeroGallery({
    onSelectPreloaded,
    onUploadImage,
    selectedGuide,
    onSelectGuide
}) {
    const fileInputRef = useRef(null);
    const scrollRef = useRef(null);
    const [isDragging, setIsDragging] = useState(false);
    const [startX, setStartX] = useState(0);
    const [scrollLeft, setScrollLeft] = useState(0);

    const [currentQuoteIndex, setCurrentQuoteIndex] = useState(0);
    const [fadeState, setFadeState] = useState(true);

    const infiniteList = [...PRELOADED_ARTWORKS, ...PRELOADED_ARTWORKS];

    useEffect(() => {
        const timer = setInterval(() => {
            triggerCardTransition((prev) => (prev + 1) % ART_QUOTES.length);
        }, 11000);

        return () => clearInterval(timer);
    }, []);

    const triggerCardTransition = (getNextIndex) => {
        setFadeState(false);
        setTimeout(() => {
            setCurrentQuoteIndex(getNextIndex);
            setFadeState(true);
        }, 600);
    };

    const handlePrevCard = () => {
        triggerCardTransition((prev) => (prev - 1 + ART_QUOTES.length) % ART_QUOTES.length);
    };

    const handleNextCard = () => {
        triggerCardTransition((prev) => (prev + 1) % ART_QUOTES.length);
    };

    const handleFileChange = (e) => {
        const file = e.target.files?.[0];
        if (file) {
            const reader = new FileReader();
            reader.onloadend = () => {
                onUploadImage(reader.result, file.name);
            };
            reader.readAsDataURL(file);
        }
    };

    const scrollByAmount = (distance) => {
        if (scrollRef.current) {
            scrollRef.current.scrollBy({ left: distance, behavior: 'smooth' });
        }
    };

    const handleScroll = () => {
        if (!scrollRef.current) return;
        const { scrollLeft: sLeft, scrollWidth } = scrollRef.current;
        const halfWidth = scrollWidth / 2;
        if (sLeft >= halfWidth) {
            scrollRef.current.scrollLeft = sLeft - halfWidth;
        } else if (sLeft <= 0) {
            scrollRef.current.scrollLeft = sLeft + halfWidth;
        }
    };

    const handleMouseDown = (e) => {
        setIsDragging(true);
        setStartX(e.pageX - scrollRef.current.offsetLeft);
        setScrollLeft(scrollRef.current.scrollLeft);
    };

    const handleMouseUpOrLeave = () => {
        setIsDragging(false);
    };

    const handleMouseMove = (e) => {
        if (!isDragging) return;
        e.preventDefault();
        const x = e.pageX - scrollRef.current.offsetLeft;
        const walk = (x - startX) * 1.5;
        scrollRef.current.scrollLeft = scrollLeft - walk;
    };

    const activeQuote = ART_QUOTES[currentQuoteIndex];

    return (
        <div className="py-4 px-2 sm:px-6 max-w-7xl mx-auto space-y-12">

            {/* 1. Header */}
            <section className="text-center max-w-4xl mx-auto space-y-4 pt-4">
                <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-amber-50 dark:bg-amber-950/60 border border-amber-200 dark:border-amber-900/40 text-amber-800 dark:text-amber-300 text-xs font-medium tracking-widest uppercase shadow-sm">
                    <Sparkles className="w-3.5 h-3.5 text-amber-600" />
                    <span>Interactive Digital Museum Experience</span>
                </div>

                <h1 className="font-serif text-5xl sm:text-7xl md:text-8xl font-bold tracking-tight text-stone-900 dark:text-stone-50 leading-none">
                    KalaKatha <span className="font-sans font-light text-amber-600 dark:text-amber-500 text-3xl sm:text-5xl align-top">AI</span>
                </h1>

                <p className="text-base sm:text-xl font-serif italic text-stone-600 dark:text-stone-300 max-w-2xl mx-auto">
                    “Don’t just look at art. Step inside it.”
                </p>
            </section>

            {/* 2. Exhibition Reel -> id="gallery" */}
            <section id="gallery" className="space-y-4">
                <div className="flex items-end justify-between px-2">
                    <div>
                        <h2 className="text-2xl sm:text-4xl font-serif text-stone-900 dark:text-stone-100 font-medium tracking-tight">
                            Whose story will you enter?
                        </h2>
                        <p className="text-sm text-stone-500 dark:text-stone-400 mt-1">
                            Select an exhibition piece to explore or drag horizontally
                        </p>
                    </div>

                    <div className="flex items-center gap-2">
                        <button
                            onClick={() => scrollByAmount(-350)}
                            className="p-2.5 rounded-full border border-stone-200 dark:border-stone-800 bg-white dark:bg-stone-900 hover:bg-stone-100 dark:hover:bg-stone-800 text-stone-700 dark:text-stone-300 shadow-sm transition active:scale-95 cursor-pointer"
                            aria-label="Scroll left"
                        >
                            <ChevronLeft className="w-4 h-4" />
                        </button>
                        <button
                            onClick={() => scrollByAmount(350)}
                            className="p-2.5 rounded-full border border-stone-200 dark:border-stone-800 bg-white dark:bg-stone-900 hover:bg-stone-100 dark:hover:bg-stone-800 text-stone-700 dark:text-stone-300 shadow-sm transition active:scale-95 cursor-pointer"
                            aria-label="Scroll right"
                        >
                            <ChevronRight className="w-4 h-4" />
                        </button>
                    </div>
                </div>

                <div
                    ref={scrollRef}
                    onScroll={handleScroll}
                    onMouseDown={handleMouseDown}
                    onMouseUp={handleMouseUpOrLeave}
                    onMouseLeave={handleMouseUpOrLeave}
                    onMouseMove={handleMouseMove}
                    className={`flex gap-6 overflow-x-auto py-6 px-2 no-scrollbar select-none ${isDragging ? 'cursor-grabbing' : 'cursor-grab'
                        }`}
                    style={{ scrollBehavior: isDragging ? 'auto' : 'smooth' }}
                >
                    {infiniteList.map((art, index) => (
                        <div
                            key={`${art.id}-${index}`}
                            onClick={() => {
                                if (!isDragging) onSelectPreloaded(art);
                            }}
                            className="w-72 sm:w-80 h-[440px] flex-shrink-0 group relative rounded-3xl overflow-hidden bg-stone-900 shadow-lg hover:shadow-2xl transition-all duration-500 ease-out border border-stone-200/60 dark:border-stone-800/80 hover:-translate-y-2 hover:border-amber-500/50 cursor-pointer"
                        >
                            <img
                                src={art.image}
                                alt={art.title}
                                className="w-full h-full object-cover transition-transform duration-700 ease-out group-hover:scale-105 group-hover:brightness-95"
                                loading="lazy"
                                draggable={false}
                            />

                            <div className="absolute inset-0 bg-gradient-to-t from-black/95 via-black/35 to-transparent flex flex-col justify-end p-6 text-white transition-opacity duration-300">
                                <span className="text-[11px] uppercase tracking-wider text-amber-300 font-medium">
                                    {art.artist}
                                </span>
                                <h3 className="font-serif text-xl sm:text-2xl font-semibold leading-tight line-clamp-1 mt-1">
                                    {art.title}
                                </h3>
                                <p className="text-xs text-stone-300 line-clamp-2 mt-2 leading-relaxed opacity-85 group-hover:opacity-100 transition-opacity">
                                    {art.description}
                                </p>
                                <div className="mt-4 flex items-center gap-2 text-xs font-medium text-amber-400">
                                    <span>Step inside</span>
                                    <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1.5 transition-transform duration-300" />
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </section>

            {/* 3. Choose Guide Persona -> id="guides" */}
            <section id="guides" className="pt-6 border-t border-stone-200/80 dark:border-stone-800/80">
                <GuideSelector selectedGuide={selectedGuide} onSelectGuide={onSelectGuide} />
            </section>

            {/* 4. Upload Artwork -> id="upload" */}
            <section id="upload" className="pt-6">
                <div
                    onClick={() => fileInputRef.current?.click()}
                    className="group relative border-2 border-dashed border-stone-300 dark:border-stone-700 hover:border-amber-600 dark:hover:border-amber-500 rounded-3xl p-8 sm:p-12 text-center cursor-pointer bg-white/40 dark:bg-stone-900/40 hover:bg-stone-50/80 dark:hover:bg-stone-900/80 transition-all duration-300 shadow-sm"
                >
                    <input
                        type="file"
                        ref={fileInputRef}
                        onChange={handleFileChange}
                        accept="image/*"
                        className="hidden"
                    />
                    <div className="flex flex-col items-center gap-3">
                        <div className="w-14 h-14 rounded-full bg-stone-100 dark:bg-stone-800 group-hover:scale-105 flex items-center justify-center transition-transform">
                            <Upload className="w-6 h-6 text-stone-700 dark:text-stone-200" />
                        </div>
                        <div>
                            <span className="font-serif text-xl font-medium text-stone-900 dark:text-stone-100">
                                Or Upload Any Human Artwork
                            </span>
                            <p className="text-xs text-stone-500 dark:text-stone-400 mt-1">
                                Drop your image here or click to browse (JPG, PNG, WebP)
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            {/* 5. Editorial Archival Flashcard -> id="quotes" */}
            <section id="quotes" className="pt-8 pb-10 border-t border-stone-200/80 dark:border-stone-800/80 max-w-4xl mx-auto">
                <div className="relative rounded-3xl border border-stone-200 dark:border-stone-800 bg-white/70 dark:bg-stone-900/60 backdrop-blur-md p-8 sm:p-12 shadow-sm transition-all duration-300">
                    <div className="absolute top-4 left-4 text-stone-300 dark:text-stone-700">
                        <Quote className="w-8 h-8 opacity-30 rotate-180" />
                    </div>

                    <div className="flex items-center justify-between border-b border-stone-100 dark:border-stone-800 pb-4 mb-6">
                        <div className="flex items-center gap-2 text-[11px] uppercase tracking-widest text-amber-700 dark:text-amber-400 font-semibold">
                            <Compass className="w-3.5 h-3.5" />
                            <span>Artist Meditation • Card {currentQuoteIndex + 1} of {ART_QUOTES.length}</span>
                        </div>

                        <div className="flex items-center gap-1.5">
                            <button
                                onClick={handlePrevCard}
                                className="p-1.5 rounded-lg border border-stone-200 dark:border-stone-800 hover:bg-stone-100 dark:hover:bg-stone-800 text-stone-600 dark:text-stone-400 transition cursor-pointer"
                                aria-label="Previous card"
                            >
                                <ChevronLeft className="w-4 h-4" />
                            </button>
                            <button
                                onClick={handleNextCard}
                                className="p-1.5 rounded-lg border border-stone-200 dark:border-stone-800 hover:bg-stone-100 dark:hover:bg-stone-800 text-stone-600 dark:text-stone-400 transition cursor-pointer"
                                aria-label="Next card"
                            >
                                <ChevronRight className="w-4 h-4" />
                            </button>
                        </div>
                    </div>

                    <div
                        className={`min-h-[160px] flex flex-col justify-center text-center space-y-5 transition-all duration-1000 ease-in-out transform ${fadeState
                            ? 'opacity-100 translate-y-0 filter blur-0 scale-100'
                            : 'opacity-0 translate-y-1.5 filter blur-[2px] scale-[0.99]'
                            }`}
                    >
                        <blockquote className="font-serif text-2xl sm:text-3xl md:text-4xl text-stone-800 dark:text-stone-100 font-normal leading-relaxed max-w-3xl mx-auto">
                            “{activeQuote.quote}”
                        </blockquote>

                        <div className="space-y-1 pt-2">
                            <div className="font-sans text-xs sm:text-sm font-semibold tracking-widest uppercase text-stone-900 dark:text-stone-100">
                                {activeQuote.author}
                            </div>
                            <div className="text-xs text-amber-700 dark:text-amber-400 font-serif italic">
                                {activeQuote.era} • {activeQuote.context}
                            </div>
                        </div>
                    </div>

                    <div className="mt-8 pt-4 border-t border-stone-100 dark:border-stone-800 flex items-center justify-between text-[11px] text-stone-400 dark:text-stone-500">
                        <span>Archival Reflection</span>
                        <div className="w-32 h-1 bg-stone-100 dark:bg-stone-800 rounded-full overflow-hidden">
                            <div
                                className="h-full bg-amber-600/80 transition-all duration-700 ease-out"
                                style={{ width: `${((currentQuoteIndex + 1) / ART_QUOTES.length) * 100}%` }}
                            />
                        </div>
                    </div>
                </div>
            </section>

            {/* 6. Artist Spotlight (#artists) */}
            <div id="artists" className="pt-2">
                <ArtistSpotlight
                    onSelectArtwork={(image, title) => {
                        // Find which artist corresponds to this artwork title
                        onSelectPreloaded({
                            image,
                            title,
                            artistProfile: {
                                name: title.includes('Mona Lisa') ? 'Leonardo da Vinci' :
                                    title.includes('Starry Night') ? 'Vincent van Gogh' :
                                        title.includes('Guernica') ? 'Pablo Picasso' :
                                            title.includes('Water Lilies') ? 'Claude Monet' : 'Johannes Vermeer',
                                movement: title.includes('Mona Lisa') ? 'High Renaissance' :
                                    title.includes('Starry Night') ? 'Post-Impressionism' :
                                        title.includes('Guernica') ? 'Cubism' :
                                            title.includes('Water Lilies') ? 'Impressionism' : 'Dutch Golden Age',
                                years: title.includes('Mona Lisa') ? '1452 – 1519' :
                                    title.includes('Starry Night') ? '1853 – 1890' :
                                        title.includes('Guernica') ? '1881 – 1973' :
                                            title.includes('Water Lilies') ? '1840 – 1926' : '1632 – 1675',
                                origin: title.includes('Mona Lisa') ? 'Vinci, Italy' :
                                    title.includes('Starry Night') ? 'Zundert, Netherlands' :
                                        title.includes('Guernica') ? 'Málaga, Spain' :
                                            title.includes('Water Lilies') ? 'Paris, France' : 'Delft, Netherlands',
                                description: title.includes('Mona Lisa') ? 'Universal Renaissance polymath and master of sfumato, renowned for harmonizing scientific anatomical precision with poetic human emotion.' :
                                    title.includes('Starry Night') ? 'Post-impressionist pioneer who revolutionized modern art by channeling raw psychological devotion through rhythmic impasto brushcraft and vibrant color contrast.' :
                                        title.includes('Guernica') ? 'Modernist revolutionary who dismantled centuries of perspective to co-invent Cubism, deconstructing subjects into colliding geometric planes.' :
                                            title.includes('Water Lilies') ? 'Forefather of French Impressionism whose practice dissolved rigid studio outlines into shimmering optical vibrations of natural light and atmosphere.' :
                                                'Delft master celebrated for optical precision, radiant specular lighting, and rich lapis lazuli glazes depicting intimate domestic serenity.',
                                famousWork: {
                                    title: title,
                                    year: title.includes('Mona Lisa') ? '1503' :
                                        title.includes('Starry Night') ? '1889' :
                                            title.includes('Guernica') ? '1937' :
                                                title.includes('Water Lilies') ? '1899' : '1665',
                                    museum: title.includes('Mona Lisa') ? 'Musée du Louvre, Paris' :
                                        title.includes('Starry Night') ? 'Museum of Modern Art (MoMA), New York' :
                                            title.includes('Guernica') ? 'Museo Reina Sofía, Madrid' :
                                                title.includes('Water Lilies') ? 'Musée de l’Orangerie, Paris' : 'Mauritshuis, The Hague'
                                }
                            }
                        });
                    }}
                />
            </div>

            {/* 7. About & Mission -> id="about" */}
            <div id="about" className="pt-2">
                <AboutUsSection />
            </div>
            {/* In your Hero or Section backdrop */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[650px] h-[350px] bg-gradient-to-tr from-amber-400/10 via-amber-200/5 to-transparent rounded-full blur-3xl pointer-events-none -z-10" />
        </div>
    );
}


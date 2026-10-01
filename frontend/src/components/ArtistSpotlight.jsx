import React, { useState } from 'react';
import { Palette, MapPin, Calendar, Building2, Award } from 'lucide-react';

const ARTISTS = [
    {
        id: 'da-vinci',
        name: 'Leonardo da Vinci',
        alias: 'Da Vinci',
        years: '1452 – 1519',
        origin: 'Vinci, Italy',
        movement: 'High Renaissance',
        portrait: 'https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=800&q=80',
        description: 'Universal Renaissance polymath and master of sfumato, renowned for harmonizing scientific anatomical precision with poetic human emotion.',
        famousWork: {
            title: 'Mona Lisa',
            year: '1503',
            museum: 'Musée du Louvre, Paris',
            image: 'https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=800&q=80'
        }
    },
    {
        id: 'van-gogh',
        name: 'Vincent van Gogh',
        alias: 'Van Gogh',
        years: '1853 – 1890',
        origin: 'Zundert, Netherlands',
        movement: 'Post-Impressionism',
        portrait: 'https://images.unsplash.com/photo-1579783902614-a3fb3927b675?auto=format&fit=crop&w=800&q=80',
        description: 'Post-impressionist pioneer who revolutionized modern art by channeling raw psychological devotion through rhythmic impasto brushcraft and vibrant color contrast.',
        famousWork: {
            title: 'The Starry Night',
            year: '1889',
            museum: 'Museum of Modern Art (MoMA), New York',
            image: 'https://images.unsplash.com/photo-1579783902614-a3fb3927b675?auto=format&fit=crop&w=800&q=80'
        }
    },
    {
        id: 'picasso',
        name: 'Pablo Picasso',
        alias: 'Picasso',
        years: '1881 – 1973',
        origin: 'Málaga, Spain',
        movement: 'Cubism',
        portrait: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=800&q=80',
        description: 'Modernist revolutionary who dismantled centuries of perspective to co-invent Cubism, deconstructing subjects into colliding geometric planes.',
        famousWork: {
            title: 'Guernica',
            year: '1937',
            museum: 'Museo Reina Sofía, Madrid',
            image: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=800&q=80'
        }
    },
    {
        id: 'monet',
        name: 'Claude Monet',
        alias: 'Monet',
        years: '1840 – 1926',
        origin: 'Paris, France',
        movement: 'Impressionism',
        portrait: 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=800&q=80',
        description: 'Forefather of French Impressionism whose practice dissolved rigid studio outlines into shimmering optical vibrations of natural light and atmosphere.',
        famousWork: {
            title: 'Water Lilies',
            year: '1899',
            museum: 'Musée de l’Orangerie, Paris',
            image: 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=800&q=80'
        }
    },
    {
        id: 'vermeer',
        name: 'Johannes Vermeer',
        alias: 'Vermeer',
        years: '1632 – 1675',
        origin: 'Delft, Netherlands',
        movement: 'Dutch Golden Age',
        portrait: 'https://images.unsplash.com/photo-1578925518470-4def7a0f08bb?auto=format&fit=crop&w=800&q=80',
        description: 'Delft master celebrated for optical precision, radiant specular lighting, and rich lapis lazuli glazes depicting intimate domestic serenity.',
        famousWork: {
            title: 'Girl with a Pearl Earring',
            year: '1665',
            museum: 'Mauritshuis, The Hague',
            image: 'https://images.unsplash.com/photo-1578925518470-4def7a0f08bb?auto=format&fit=crop&w=800&q=80'
        }
    }
];

export default function ArtistSpotlight({ artists = ARTISTS }) {
    const [selectedIndex, setSelectedIndex] = useState(0);
    const activeArtist = artists[selectedIndex] || artists[0];

    return (
        <section className="py-14 border-t border-stone-200 dark:border-stone-800/80 space-y-10 animate-fade-in select-none">

            {/* 1. Header with Golden Glow Pill */}
            <div className="text-center max-w-2xl mx-auto space-y-2">
                <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-800 dark:text-amber-300 text-xs font-medium tracking-widest uppercase shadow-xs">
                    <Palette className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" />
                    <span>Curated Creator Archives</span>
                </div>
                <h2 className="text-3xl sm:text-5xl font-serif text-stone-900 dark:text-stone-100 font-medium tracking-tight">
                    Who's your favorite?
                </h2>
                <p className="text-xs sm:text-sm text-stone-500 dark:text-stone-400">
                    Select an artist to view their background and signature work
                </p>
            </div>

            {/* 2. Top Five Artist Selector Deck */}
            <div className="max-w-5xl mx-auto px-4">
                <div className="flex items-center justify-center gap-4 sm:gap-6 flex-wrap py-2">
                    {artists.map((artist, idx) => {
                        const isSelected = selectedIndex === idx;

                        return (
                            <button
                                key={artist.id || idx}
                                type="button"
                                onClick={() => setSelectedIndex(idx)}
                                className={`group relative text-left rounded-3xl overflow-hidden cursor-pointer transition-all duration-500 ease-out transform focus:outline-none ${isSelected
                                        ? 'w-36 sm:w-44 h-56 sm:h-64 -translate-y-3 scale-105 shadow-2xl ring-2 ring-amber-500 border border-amber-500 z-20'
                                        : 'w-34 sm:w-40 h-52 sm:h-60 opacity-80 hover:opacity-100 hover:-translate-y-1 hover:shadow-xl border border-stone-200/80 dark:border-stone-800 z-10'
                                    } active:scale-95`}
                            >
                                <img
                                    src={artist.portrait}
                                    alt={artist.name}
                                    referrerPolicy="no-referrer"
                                    className={`w-full h-full object-cover transition-transform duration-700 ease-out ${isSelected ? 'scale-110 filter brightness-105' : 'group-hover:scale-105'
                                        }`}
                                    draggable={false}
                                />

                                <div className="absolute inset-0 bg-gradient-to-t from-black/95 via-black/35 to-transparent flex flex-col justify-end p-4 text-white">
                                    <span className="font-serif text-base sm:text-lg font-semibold tracking-wide leading-tight">
                                        {artist.alias || artist.name}
                                    </span>
                                    <span className="text-[11px] text-amber-300 font-medium tracking-wide mt-1">
                                        {artist.movement}
                                    </span>
                                </div>
                            </button>
                        );
                    })}
                </div>
            </div>

            {/* 3. Detailed Master Artist Card & Archival Preview */}
            {activeArtist && (
                <div className="max-w-5xl mx-auto rounded-3xl border border-stone-200/90 dark:border-stone-800 bg-white/80 dark:bg-stone-900/70 backdrop-blur-xl p-6 sm:p-9 shadow-xl transition-all duration-500">
                    <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-center">

                        {/* Left Column: Biography, Era & Museum Location */}
                        <div className="md:col-span-7 space-y-4">
                            <div className="space-y-1">
                                <span className="inline-block text-[11px] uppercase tracking-widest font-semibold text-amber-700 dark:text-amber-400">
                                    {activeArtist.movement}
                                </span>
                                <h3 className="font-serif text-3xl sm:text-4xl font-bold text-stone-900 dark:text-stone-100 tracking-tight">
                                    {activeArtist.name}
                                </h3>
                            </div>

                            {/* Dates & Origin */}
                            <div className="flex flex-wrap gap-4 text-xs text-stone-500 dark:text-stone-400 font-medium">
                                <span className="flex items-center gap-1.5">
                                    <Calendar className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" />
                                    {activeArtist.years}
                                </span>
                                <span className="flex items-center gap-1.5">
                                    <MapPin className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" />
                                    {activeArtist.origin}
                                </span>
                            </div>

                            {/* Full Artist Bio Description */}
                            <p className="text-xs sm:text-sm font-serif leading-relaxed text-stone-700 dark:text-stone-300">
                                {activeArtist.description}
                            </p>

                            {/* Preserved Museum & Signature Work Badge */}
                            <div className="p-3.5 rounded-2xl bg-amber-50/60 dark:bg-amber-950/30 border border-amber-200/70 dark:border-amber-900/50 space-y-1.5 text-xs">
                                <div className="flex items-center gap-1.5 text-amber-900 dark:text-amber-200 font-semibold">
                                    <Award className="w-3.5 h-3.5 text-amber-600" />
                                    <span>
                                        Signature Masterwork: {activeArtist.famousWork?.title} ({activeArtist.famousWork?.year})
                                    </span>
                                </div>
                                <div className="flex items-center gap-1.5 text-stone-600 dark:text-stone-400 text-[11px]">
                                    <Building2 className="w-3.5 h-3.5 text-stone-500" />
                                    <span>
                                        Preserved at: <strong className="text-stone-700 dark:text-stone-300">{activeArtist.famousWork?.museum}</strong>
                                    </span>
                                </div>
                            </div>
                        </div>

                        {/* Right Column: Signature Work Preview Canvas (View Only) */}
                        <div className="md:col-span-5">
                            <div className="rounded-2xl overflow-hidden border border-stone-200 dark:border-stone-800 bg-stone-950 shadow-lg relative aspect-[4/3]">
                                <img
                                    src={activeArtist.famousWork?.image}
                                    alt={activeArtist.famousWork?.title}
                                    referrerPolicy="no-referrer"
                                    className="w-full h-full object-cover"
                                />
                                <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/30 to-transparent flex flex-col justify-end p-4 text-white">
                                    <span className="text-[10px] uppercase tracking-wider text-amber-300 font-semibold">
                                        Signature Piece
                                    </span>
                                    <span className="font-serif text-sm sm:text-base font-semibold truncate">
                                        {activeArtist.famousWork?.title} ({activeArtist.famousWork?.year})
                                    </span>
                                    <span className="text-[11px] text-stone-300 opacity-90 line-clamp-1 mt-0.5">
                                        {activeArtist.famousWork?.museum}
                                    </span>
                                </div>
                            </div>
                        </div>

                    </div>
                </div>
            )}

        </section>
    );
}
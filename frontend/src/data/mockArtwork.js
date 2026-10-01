export const PRELOADED_ARTWORKS = [
    {
        id: "starry-night",
        title: "The Starry Night",
        artist: "Vincent van Gogh (1889)",
        image: "https://images.unsplash.com/photo-1541701494587-cb58502866ab?auto=format&fit=crop&w=1200&q=80",
        description: "Post-impressionist swirling night sky over Saint-Rémy."
    },
    {
        id: "mona-lisa",
        title: "Portrait of Lisa Gherardini",
        artist: "Leonardo da Vinci (1503)",
        image: "https://images.unsplash.com/photo-1561214115-f2f134cc4912?auto=format&fit=crop&w=1200&q=80",
        description: "The enigmatic Renaissance masterpiece exhibiting sfumato technique."
    },
    {
        id: "great-wave",
        title: "Under the Wave off Kanagawa",
        artist: "Katsushika Hokusai (1831)",
        image: "https://images.unsplash.com/photo-1582561424760-0321d75e81fa?auto=format&fit=crop&w=1200&q=80",
        description: "Iconic ukiyo-e woodblock print framing Mount Fuji."
    },
    {
        id: "girl-pearl-earring",
        title: "Girl with a Pearl Earring",
        artist: "Johannes Vermeer (1665)",
        image: "https://images.unsplash.com/photo-1578925518470-4def7a0f08bb?auto=format&fit=crop&w=1200&q=80",
        description: "Dutch Golden Age tronie featuring intimate lighting and exotic turban."
    },
    {
        id: "wanderer-sea-fog",
        title: "Wanderer above the Sea of Fog",
        artist: "Caspar David Friedrich (1818)",
        image: "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1200&q=80",
        description: "Romantic contemplation atop rugged alpine precipice."
    },
    {
        id: "water-lilies",
        title: "Water Lilies & Japanese Bridge",
        artist: "Claude Monet (1899)",
        image: "https://images.unsplash.com/photo-1577083552431-6e5fd01aa342?auto=format&fit=crop&w=1200&q=80",
        description: "Impressionist study of light and tranquil reflection at Giverny."
    },
    {
        id: "klimt-the-kiss",
        title: "The Kiss",
        artist: "Gustav Klimt (1908)",
        image: "https://images.unsplash.com/photo-1580136579312-94651dfd596d?auto=format&fit=crop&w=1200&q=80",
        description: "Vienna Secession gilded embrace of decorative symbolism."
    }
];

export const ARTWORK_DATABASE = {
    "the starry night": {
        visual_analysis: {
            objects: ["Flame-like Cypress Tree", "Village Church Spire", "Rolling Alpilles Mountains", "Eleven Swirling Stars", "Crescent Moon"],
            people: ["Sleeping villagers (implicit)"],
            colors: ["Cobalt Blue", "Ultramarine", "Zinc White", "Indian Yellow", "Viridian Deep"],
            composition: "Dynamic spiral sky balanced by a monumental vertical cypress tree commanding the left foreground.",
            mood: "Restless, transcendent, and emotionally ecstatic.",
            style: "Post-Impressionism with heavy sculptural impasto ridges."
        },
        context: {
            historical_context: "Painted from the barred room of the Saint-Paul-de-Mausole asylum in Saint-Rémy-de-Provence in June 1889 after an acute breakdown.",
            cultural_context: "Marked a revolutionary rupture from visual observation, proving that painting could express internal psychological turmoil through pure color.",
            symbolism: "The soaring cypress represents mourning and eternal life, acting as a physical spire that anchors earthly humanity to cosmic infinity."
        },
        persona_notes: {
            professor: "Observe the deliberate non-Euclidean rhythmic vectoring: Van Gogh applies thick impasto directly from the tube to convert psychic distress into kinetic surface topography.",
            storyteller: "The midnight sky churns like a restless sea of burning stars, while a sleeping town rests unaware beneath the lonely gaze of an asylum window.",
            friendly: "Astronomers checked the night sky from 1889 and discovered that bright glowing orb next to the cypress was actually the planet Venus shining bright!",
            accessibility: "Vigorous directional topography: A dominant dark vertical pillar towers on the left, flanked by horizontal rhythmic swirling waves spanning the upper two-thirds."
        }
    },

    "starry night": {
        visual_analysis: {
            objects: ["Flame-like Cypress Tree", "Village Church Spire", "Rolling Alpilles Mountains", "Eleven Swirling Stars", "Crescent Moon"],
            people: ["Sleeping villagers (implicit)"],
            colors: ["Cobalt Blue", "Ultramarine", "Zinc White", "Indian Yellow", "Viridian Deep"],
            composition: "Dynamic spiral sky balanced by a monumental vertical cypress tree commanding the left foreground.",
            mood: "Restless, transcendent, and emotionally ecstatic.",
            style: "Post-Impressionism with heavy sculptural impasto ridges."
        },
        context: {
            historical_context: "Painted from the barred room of the Saint-Paul-de-Mausole asylum in Saint-Rémy-de-Provence in June 1889 after an acute breakdown.",
            cultural_context: "Marked a revolutionary rupture from visual observation, proving that painting could express internal psychological turmoil through pure color.",
            symbolism: "The soaring cypress represents mourning and eternal life, acting as a physical spire that anchors earthly humanity to cosmic infinity."
        },
        persona_notes: {
            professor: "Observe the deliberate non-Euclidean rhythmic vectoring: Van Gogh applies thick impasto directly from the tube to convert psychic distress into kinetic surface topography.",
            storyteller: "The midnight sky churns like a restless sea of burning stars, while a sleeping town rests unaware beneath the lonely gaze of an asylum window.",
            friendly: "Astronomers checked the night sky from 1889 and discovered that bright glowing orb next to the cypress was actually the planet Venus shining bright!",
            accessibility: "Vigorous directional topography: A dominant dark vertical pillar towers on the left, flanked by horizontal rhythmic swirling waves spanning the upper two-thirds."
        }
    },

    "girl with a pearl earring": {
        visual_analysis: {
            objects: ["Oriental Turban", "Teardrop Pearl Earring", "Ochre Jacket", "White Collar", "Black Void Background"],
            people: ["Unidentified young Dutch woman (Tronie study)"],
            colors: ["Ultramarine Blue", "Lead Tin Yellow", "Bone Black", "Alizarin Crimson", "Pearl Luster White"],
            composition: "Intimate three-quarter portrait turned over the left shoulder against a dramatic dark backdrop.",
            mood: "Quietly captivating, poised between intimacy and mystery.",
            style: "Dutch Golden Age Baroque with delicate camera obscura optical glazes."
        },
        context: {
            historical_context: "Painted in Delft around 1665 during the zenith of the Dutch Golden Age. It is not an individual portrait, but a 'tronie'—a study of character, costume, and expression.",
            cultural_context: "The exotic turban symbolizes the Dutch Republic's worldwide maritime trade networks and fascination with Eastern luxury goods.",
            symbolism: "The pearl functions as an optical jewel of purity and wealth, painted with merely two rapid, translucent dabs of white pigment."
        },
        persona_notes: {
            professor: "Notice the elimination of spatial contour lines around her jaw; Vermeer relies purely on value transitions and pigment glaze refraction rather than drawing outlines.",
            storyteller: "She freezes mid-breath as if about to murmur a forgotten confession, illuminated only by a fleeting ray cutting through the quiet shadows of Delft.",
            friendly: "Check out that massive pearl—it isn't even painted solid! It's basically two clever dots of white paint that trick your eyes into seeing a glowing gem.",
            accessibility: "High focal contrast: A softly lit facial profile positioned off-center left, wearing a blue-and-gold headwrap, contrasting against an absolute matte black void."
        }
    },

    "mona lisa": {
        visual_analysis: {
            objects: ["Balcony Balustrade", "Meandering River", "Jagged Alpine Peaks", "Translucent Guimpe Veil", "Pleated Silk Robe"],
            people: ["Lisa Gherardini del Giocondo"],
            colors: ["Burnt Umber", "Terra Verde", "Raw Sienna", "Atmospheric Haze Gray", "Muted Olive"],
            composition: "Pyramidal seated figure in three-quarter view with hands folded in the foreground beneath an aerial perspective landscape.",
            mood: "Serene, psychologically aloof, and deeply meditative.",
            style: "High Renaissance with microscopic sfumato oil glazing."
        },
        context: {
            historical_context: "Commissioned in Florence around 1503 by merchant Francesco del Giocondo, Da Vinci kept and revised this portrait across multiple decades.",
            cultural_context: "Epitomizes Italian Renaissance Humanism, mirroring the intricate anatomy of the human soul directly against the natural architecture of the earth.",
            symbolism: "The winding waterways and earthen roads behind her correspond directly to the arterial veins and skeletal framework of the human body."
        },
        persona_notes: {
            professor: "The absence of sharp focal edges around the ocular corners and oral commissures creates a dynamic psychological ambiguity that changes with peripheral fixation.",
            storyteller: "Centuries fade into the smoky twilight behind her, as an unreadable half-smile guards secrets that have outlasted empires and monarchs.",
            friendly: "Did you spot her missing eyebrows? Plucking them was peak high-society fashion in Renaissance Italy, and Leonardo layered 30+ sheer paint coats over her face!",
            accessibility: "Stable seated pyramid layout: Central warm-toned torso and resting hands anchor the bottom foreground, while an ethereal pale-blue horizon recedes into the upper third."
        }
    },

    "portrait of lisa gherardini": {
        visual_analysis: {
            objects: ["Balcony Balustrade", "Meandering River", "Jagged Alpine Peaks", "Translucent Guimpe Veil", "Pleated Silk Robe"],
            people: ["Lisa Gherardini del Giocondo"],
            colors: ["Burnt Umber", "Terra Verde", "Raw Sienna", "Atmospheric Haze Gray", "Muted Olive"],
            composition: "Pyramidal seated figure in three-quarter view with hands folded in the foreground beneath an aerial perspective landscape.",
            mood: "Serene, psychologically aloof, and deeply meditative.",
            style: "High Renaissance with microscopic sfumato oil glazing."
        },
        context: {
            historical_context: "Commissioned in Florence around 1503 by merchant Francesco del Giocondo, Da Vinci kept and revised this portrait across multiple decades.",
            cultural_context: "Epitomizes Italian Renaissance Humanism, mirroring the intricate anatomy of the human soul directly against the natural architecture of the earth.",
            symbolism: "The winding waterways and earthen roads behind her correspond directly to the arterial veins and skeletal framework of the human body."
        },
        persona_notes: {
            professor: "The absence of sharp focal edges around the ocular corners and oral commissures creates a dynamic psychological ambiguity that changes with peripheral fixation.",
            storyteller: "Centuries fade into the smoky twilight behind her, as an unreadable half-smile guards secrets that have outlasted empires and monarchs.",
            friendly: "Did you spot her missing eyebrows? Plucking them was peak high-society fashion in Renaissance Italy, and Leonardo layered 30+ sheer paint coats over her face!",
            accessibility: "Stable seated pyramid layout: Central warm-toned torso and resting hands anchor the bottom foreground, while an ethereal pale-blue horizon recedes into the upper third."
        }
    },

    "under the wave off kanagawa": {
        visual_analysis: {
            objects: ["Clawing Wave Crests", "Mount Fuji", "Three Cargo Boats (Oshiokuri-bune)", "Sea Foam Droplets", "Prussian Blue Gradients"],
            people: ["Oarsmen clinging to boats"],
            colors: ["Prussian Blue", "Indigo", "Pale Ochre", "Bokashi Sky Gray", "Sea Foam White"],
            composition: "Fractal sweeping curve dominating the left and arching over the static triangular silhouette of Mount Fuji.",
            mood: "Dramatic, visceral, timeless, and perilous.",
            style: "Ukiyo-e Woodblock Print (Meisho-e)."
        },
        context: {
            historical_context: "Published in Japan in late 1831 as the first print of Hokusai's series 'Thirty-Six Views of Mount Fuji' during the late Edo period.",
            cultural_context: "Reflects the introduction of imported European synthetic Prussian blue pigment and early Western perspective into Japanese woodblock art.",
            symbolism: "The violent, transient power of the surging wave contrasts against the eternal stillness of sacred Mount Fuji."
        },
        persona_notes: {
            professor: "Hokusai synthesizes Dutch linear perspective with traditional Japanese decorative flattening, using the logarithmic spiral of the wave to frame the vanishing point on Fuji.",
            storyteller: "A towering wall of white water claws at the sky, threatening to swallow the fragile wooden boats while eternal Fuji watches silently in the distance.",
            friendly: "Those aren't just random splashes—Hokusai carved the foam tips like ferocious eagle claws ready to strike the boat crews!",
            accessibility: "High dynamic movement: A colossal cresting wave frames the upper-left, plunging down toward low, long boats, balanced by a tiny serene mountain triangle in the center-distance."
        }
    },

    "wanderer above the sea of fog": {
        visual_analysis: {
            objects: ["Rückenfigur Solitary Traveler", "Craggy Basalt Precipice", "Blanket of Dense Fog", "Distant Mountain Peaks"],
            people: ["Gentleman in dark overcoat viewed from behind"],
            colors: ["Slate Gray", "Vapour Blue", "Forest Shadow Green", "Mist White", "Charcoal Black"],
            composition: "Central triangular solitary silhouette commanding a rocky pinnacle, staring outward over a vast misty horizon.",
            mood: "Sublime, awe-inspiring, and solitary.",
            style: "German Romanticism."
        },
        context: {
            historical_context: "Painted by Caspar David Friedrich in Dresden in 1818 in the wake of the Napoleonic Wars.",
            cultural_context: "The definitive masterpiece of the Romantic 'Sublime'—evoking existential awe and human vulnerability before nature's grandeur.",
            symbolism: "The swirling ocean of mist represents the unknown journey of human destiny and the mysterious veil of eternity."
        },
        persona_notes: {
            professor: "The deliberate 'Rückenfigur' framing deprives the spectator of facial empathy, forcing our gaze to adopt the traveler’s exact ocular vantage point.",
            storyteller: "Standing upon the edge of the world, a lone wanderer watches kingdoms of cloud roll silently over the silent alpine ridges.",
            friendly: "The mountains in the background aren't from one single location; Friedrich hiked all over Saxon Switzerland and stitched together different peaks into one view!",
            accessibility: "Centered triangular focal anchor: A solid, dark silhouette commands the immediate foreground, splitting a wide expanse of pale white-and-gray mist."
        }
    },

    "water lilies": {
        visual_analysis: {
            objects: ["Floating Nymphaea Blossoms", "Drooping Willow Shadows", "Reflective Water Surface", "Submerged Reeds"],
            people: ["None (Pure Botanical Nature)"],
            colors: ["Emerald Green", "Lavender Violet", "Pale Rose", "Cerulean Blue", "Sunlit Primrose"],
            composition: "Horizonless close-up field where sky reflections, surface lilies, and water depths merge into a continuous pictorial plane.",
            mood: "Tranquil, meditative, and sensory.",
            style: "Late French Impressionism exploring the dissolution of physical form into pure light."
        },
        context: {
            historical_context: "Painted in Monet’s custom-engineered water garden in Giverny between 1899 and 1919 while he battled cataracts.",
            cultural_context: "Dissolved 19th-century realism into environmental abstraction, laying the cornerstone for post-war modern American abstract art.",
            symbolism: "The floating aquatic blooms symbolize transient moments suspended over the fluid, bottomless flow of time."
        },
        persona_notes: {
            professor: "By abolishing both horizon and shoreline anchor points, Monet forces the retinal gaze into an infinite planar surface where optical reflection replaces volumetric weight.",
            storyteller: "Drift along the quiet waters of Giverny, where clouds and blossoms float together in a dream of violet reflections and gentle breezes.",
            friendly: "Monet loved these plants so much he redirected an entire local river to create his private lily pond, even hiring a gardener whose only job was dusting them off!",
            accessibility: "Homogeneous textural field: A fluid spread of pastel greens and muted lilacs dotted with soft, isolated floral clusters across the middle plane."
        }
    },

    "the kiss": {
        visual_analysis: {
            objects: ["Ornamental Gilded Mantle", "Wildflower Cliff Edge", "Halo of Gold Leaf", "Geometric Rectangles", "Floral Spirals"],
            people: ["Embraced lovers"],
            colors: ["Burnished Gold Leaf", "Bronze Ochre", "Meadow Green", "Lavender", "Poppy Crimson"],
            composition: "Compact vertical pillar of draped figures kneeling precariously upon a verdant cliff top against a bronze sky.",
            mood: "Sensual, transcendent, sacred, and opulent.",
            style: "Vienna Secession Symbolism / Art Nouveau."
        },
        context: {
            historical_context: "Created by Gustav Klimt in Vienna between 1907 and 1908 at the height of his acclaimed 'Golden Phase'.",
            cultural_context: "Rebelled against conservative academic aesthetics by resurrecting Byzantine mosaic craft to celebrate modern intimacy and human passion.",
            symbolism: "The man’s cloak bears angular black-and-white rectangles representing structured masculinity, while the woman’s gown displays soft, colorful floral circles."
        },
        persona_notes: {
            professor: "Notice the synthesis of two-dimensional flat ornamentation and three-dimensional flesh: Klimt juxtaposes naturalistic portraits inside an abstract planar tapestry.",
            storyteller: "Enfolded in an armor of hammered gold and wild flowers, two lovers dissolve into an eternal embrace at the edge of the world.",
            friendly: "That isn't yellow paint—Klimt applied sheets of actual 24-karat gold leaf, inspired by radiant church mosaics he marveled at in Italy!",
            accessibility: "Vertical radiant center: A towering, high-contrast golden silhouette grounded in the lower quadrant by a colorful textured meadow."
        }
    }
};

export const MOCK_ANALYSIS_RESPONSE = ARTWORK_DATABASE["the starry night"];

export function getPersonaSpecificMock(title = "", persona = 'storyteller') {
    const normalizedTitle = title.toLowerCase().trim();

    let matchKey = Object.keys(ARTWORK_DATABASE).find(key =>
        normalizedTitle.includes(key) || key.includes(normalizedTitle)
    );

    const matched = matchKey ? ARTWORK_DATABASE[matchKey] : ARTWORK_DATABASE["the starry night"];

    return {
        artwork_id: matchKey || "custom_art",
        title: title || "Exhibition Masterwork",
        visual_analysis: matched.visual_analysis,
        context: matched.context,
        persona_notes: matched.persona_notes,
        current_persona: persona
    };
}
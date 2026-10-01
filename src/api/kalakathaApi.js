const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export async function analyzeArtwork(imagePayload, guide = 'storyteller') {
    const response = await fetch(`${API_BASE_URL}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: imagePayload, guide })
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData?.error?.message || 'Unable to analyze artwork. Please check the backend connection.');
    }

    return response.json();
}

export async function askArtwork(artworkId, question) {
    const response = await fetch(`${API_BASE_URL}/api/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ artwork_id: artworkId, question })
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData?.error?.message || 'Guide is unable to answer right now.');
    }

    return response.json();
}

export async function getNarration(artworkId, chapterId) {
    const response = await fetch(`${API_BASE_URL}/api/narrate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ artwork_id: artworkId, chapter_id: chapterId })
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData?.error?.message || 'Narration failed to generate.');
    }

    return response.json();
}
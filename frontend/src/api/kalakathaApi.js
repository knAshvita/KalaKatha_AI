/**
 * kalakathaApi.js — KalaKatha AI Frontend API Client
 * ══════════════════════════════════════════════════════════════════════════════
 * Centralized HTTP interface connecting the React/Vite frontend to the FastAPI
 * + Google ADK backend.
 *
 * Configured via VITE_API_BASE_URL (defaults to http://localhost:8000).
 * No API keys or backend credentials are exposed in browser code.
 * ══════════════════════════════════════════════════════════════════════════════
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Perform a backend health and liveness check.
 * GET /api/health
 */
export async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/health`);
        if (!response.ok) {
            throw new Error(`Health check returned status ${response.status}`);
        }
        return await response.json();
    } catch (err) {
        throw new Error(`Backend unavailable at ${API_BASE_URL}: ${err.message}`);
    }
}

/**
 * Convert any image input (File, Blob, Data URL, or remote URL) into a File
 * object suitable for multipart/form-data upload.
 */
export async function toImageFile(imageInput, filename = 'artwork.jpg') {
    if (imageInput instanceof File) {
        return imageInput;
    }
    if (imageInput instanceof Blob) {
        return new File([imageInput], filename, { type: imageInput.type || 'image/jpeg' });
    }
    if (typeof imageInput === 'string') {
        // Base64 Data URL
        if (imageInput.startsWith('data:')) {
            const arr = imageInput.split(',');
            const mimeMatch = arr[0].match(/:(.*?);/);
            const mime = mimeMatch ? mimeMatch[1] : 'image/jpeg';
            const bstr = atob(arr[1]);
            let n = bstr.length;
            const u8arr = new Uint8Array(n);
            while (n--) {
                u8arr[n] = bstr.charCodeAt(n);
            }
            return new File([u8arr], filename, { type: mime });
        }

        // Remote Image URL (e.g. Unsplash preloaded artwork)
        if (imageInput.startsWith('http://') || imageInput.startsWith('https://')) {
            try {
                const response = await fetch(imageInput);
                if (!response.ok) throw new Error(`Status ${response.status}`);
                const blob = await response.blob();
                return new File([blob], filename, { type: blob.type || 'image/jpeg' });
            } catch (fetchErr) {
                console.warn(`Could not fetch remote image directly, attempting fallback: ${fetchErr.message}`);
                // Return a synthesized fallback image blob if remote fetch is blocked by CORS
                const canvas = document.createElement('canvas');
                canvas.width = 600;
                canvas.height = 450;
                const ctx = canvas.getContext('2d');
                ctx.fillStyle = '#1c1917';
                ctx.fillRect(0, 0, 600, 450);
                ctx.fillStyle = '#d97706';
                ctx.font = '24px serif';
                ctx.textAlign = 'center';
                ctx.fillText(filename || 'KalaKatha Masterpiece', 300, 225);
                const blob = await new Promise((res) => canvas.toBlob(res, 'image/jpeg', 0.9));
                return new File([blob], filename, { type: 'image/jpeg' });
            }
        }
    }
    throw new Error('Unsupported image input format. Please upload a valid image file.');
}

/**
 * Upload an artwork image and initiate the 2-stage analysis pipeline.
 * POST /api/analyze (multipart/form-data)
 *
 * @param {File|Blob|string} imageInput - Binary image file or data URL
 * @param {string} guideMode - 'storyteller' | 'professor' | 'friendly' | 'accessibility'
 * @param {string} filename - Filename for the artwork
 * @returns {Promise<Object>} ArtworkAnalysisResponse
 */
export async function analyzeArtwork(imageInput, guideMode = 'storyteller', filename = 'artwork.jpg') {
    const fileObj = await toImageFile(imageInput, filename);
    const formData = new FormData();
    formData.append('file', fileObj);
    formData.append('guide_mode', guideMode.toLowerCase());

    const response = await fetch(`${API_BASE_URL}/api/analyze`, {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        let detailMsg = errorData?.detail?.error_message || errorData?.detail?.message || errorData?.detail;
        if (typeof detailMsg === 'object') {
            detailMsg = JSON.stringify(detailMsg);
        }
        if (response.status === 429) {
            throw new Error('The AI service is temporarily busy. Please wait a moment and try again.');
        }
        throw new Error(detailMsg || `Artwork analysis failed (${response.status})`);
    }

    return await response.json();
}

/**
 * Ask a natural language question about an analyzed artwork.
 * POST /api/ask (application/json)
 *
 * @param {string} sessionId - Active artwork session ID
 * @param {string} question - Question to ask
 * @returns {Promise<Object>} AskResponse
 */
export async function askQuestion(sessionId, question) {
    if (!sessionId) {
        throw new Error('Active session ID is required to ask a question.');
    }
    if (!question || !question.trim()) {
        throw new Error('Please enter a question.');
    }

    const response = await fetch(`${API_BASE_URL}/api/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: sessionId,
            question: question.trim(),
        }),
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const detailMsg = errorData?.detail || errorData?.message;
        if (response.status === 429) {
            throw new Error('AskAgent is temporarily busy with requests. Please retry in a moment.');
        }
        throw new Error(detailMsg || `AskAgent could not answer (${response.status})`);
    }

    return await response.json();
}

/** Backward-compatible alias for existing components */
export const askArtwork = (artworkId, question) => askQuestion(artworkId, question);

/**
 * Synthesize speech audio for a specific story chapter via Gemini TTS.
 * POST /api/story/audio (application/json)
 *
 * @param {string} sessionId - Active artwork session ID
 * @param {string} chapterId - Chapter identifier (e.g. 'c1' or 'chapter_1')
 * @returns {Promise<Object>} StoryAudioResponse with resolved audio_url
 */
export async function getStoryAudio(sessionId, chapterId) {
    if (!sessionId) {
        throw new Error('Active session ID is required to generate narration.');
    }

    const response = await fetch(`${API_BASE_URL}/api/story/audio`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: sessionId,
            chapter_id: chapterId,
        }),
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const detailMsg = errorData?.detail || errorData?.message;
        throw new Error(detailMsg || `Audio generation failed (${response.status})`);
    }

    const data = await response.json();

    // Resolve relative audio URLs to absolute backend URL so browser <audio> plays cleanly
    if (data.audio_url && data.audio_url.startsWith('/')) {
        data.audio_url = `${API_BASE_URL}${data.audio_url}`;
    }
    return data;
}

/** Backward-compatible alias for existing components */
export const getNarration = (artworkId, chapterId) => getStoryAudio(artworkId, chapterId);

/**
 * Validate a user's answer to a multiple-choice question against the backend.
 * POST /api/quiz/answer (application/json)
 *
 * @param {string} sessionId - Active artwork session ID
 * @param {string} questionId - Question identifier (e.g. 'q1')
 * @param {string} selectedOption - Option selected by user
 * @returns {Promise<Object>} QuizAnswerResponse
 */
export async function submitQuizAnswer(sessionId, questionId, selectedOption) {
    if (!sessionId) {
        throw new Error('Active session ID is required to verify quiz answer.');
    }

    const response = await fetch(`${API_BASE_URL}/api/quiz/answer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: sessionId,
            question_id: questionId,
            selected_option: selectedOption,
            answer: selectedOption,
        }),
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const detailMsg = errorData?.detail || errorData?.message;
        throw new Error(detailMsg || `Quiz validation failed (${response.status})`);
    }

    return await response.json();
}

/**
 * Retrieve complete stored KalaKathaExperience for an active session.
 * GET /api/session/{session_id}
 *
 * @param {string} sessionId - Session ID
 * @returns {Promise<Object>} KalaKathaExperience
 */
export async function getSession(sessionId) {
    const response = await fetch(`${API_BASE_URL}/api/session/${sessionId}`);
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData?.detail || `Session retrieval failed (${response.status})`);
    }
    return await response.json();
}
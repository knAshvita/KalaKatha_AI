import fs from 'fs';
import path from 'path';

const API_BASE_URL = 'http://127.0.0.1:8000';

async function testFullIntegration() {
    console.log("==================================================");
    console.log("FRONTEND API CLIENT: LIVE INTEGRATION TEST");
    console.log("==================================================");

    // 1. Test Health
    console.log("\n1. Testing GET /api/health...");
    const healthRes = await fetch(`${API_BASE_URL}/api/health`);
    if (!healthRes.ok) throw new Error(`Health check failed: ${healthRes.status}`);
    const health = await healthRes.json();
    console.log("   [PASS] Health OK:", health);

    // 2. Load real artwork image
    const imgPath = "C:\\Users\\Alfaz\\.gemini\\antigravity-ide\\brain\\875833a7-a719-4943-80f6-6ee0d7c1465a\\sample_artwork_1790844258587.jpg";
    if (!fs.existsSync(imgPath)) throw new Error(`Image not found: ${imgPath}`);
    const imgBuffer = fs.readFileSync(imgPath);
    console.log(`\n2. Loaded real artwork image (${imgBuffer.length} bytes)`);

    // 3. Test POST /api/analyze with multipart/form-data
    console.log("\n3. Testing POST /api/analyze with real image upload (guide_mode='storyteller')...");
    const formData = new FormData();
    const blob = new Blob([imgBuffer], { type: 'image/jpeg' });
    formData.append('file', blob, 'sample_artwork.jpg');
    formData.append('guide_mode', 'storyteller');

    const t0 = Date.now();
    const analyzeRes = await fetch(`${API_BASE_URL}/api/analyze`, {
        method: 'POST',
        body: formData,
    });

    if (!analyzeRes.ok) {
        const errText = await analyzeRes.text();
        throw new Error(`/api/analyze failed (${analyzeRes.status}): ${errText}`);
    }

    const analyzeData = await analyzeRes.json();
    const elapsed = ((Date.now() - t0) / 1000).toFixed(1);
    console.log(`   [PASS] /api/analyze succeeded in ${elapsed}s!`);
    console.log("   Session ID:", analyzeData.session_id);
    const exp = analyzeData.experience;
    console.log("   Artwork Title :", exp.artwork.title);
    console.log("   Artist        :", exp.artwork.artist);
    console.log("   Visual Focus  :", exp.visual_analysis.visual_focus);
    console.log("   Story Title   :", exp.story.story_title);
    console.log(`   Story Chapters: ${exp.story.chapters.length} chapters generated`);
    console.log(`   Quiz Questions: ${exp.learning.multiple_choice_questions.length} questions generated`);
    console.log(`   Explore Regions: ${exp.explore.regions.length} regions generated`);

    const sessionId = analyzeData.session_id;

    // 4. Test POST /api/story/audio with real Gemini TTS
    console.log("\n4. Testing POST /api/story/audio with Chapter 1...");
    const chId = exp.story.chapters[0].chapter_id;
    const audioRes = await fetch(`${API_BASE_URL}/api/story/audio`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, chapter_id: chId }),
    });

    if (!audioRes.ok) {
        const errText = await audioRes.text();
        throw new Error(`/api/story/audio failed (${audioRes.status}): ${errText}`);
    }

    const audioData = await audioRes.json();
    console.log("   [PASS] Story audio synthesized successfully!");
    console.log("   Audio URL:", audioData.audio_url);
    console.log("   Voice    :", audioData.voice);

    // Verify audio file is downloadable
    const wavUrl = `${API_BASE_URL}${audioData.audio_url}`;
    const wavRes = await fetch(wavUrl);
    if (!wavRes.ok) throw new Error(`Could not fetch WAV from ${wavUrl}`);
    const wavBuf = await wavRes.arrayBuffer();
    const header = Buffer.from(wavBuf.slice(0, 4)).toString();
    console.log(`   [PASS] Downloaded WAV (${wavBuf.byteLength} bytes, header='${header}')`);

    // 5. Test POST /api/ask with AskAgent
    console.log("\n5. Testing POST /api/ask with AskAgent...");
    const question = "Explain the symbolism of the jewelry and dress";
    const askRes = await fetch(`${API_BASE_URL}/api/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, question }),
    });

    if (!askRes.ok) {
        const errText = await askRes.text();
        throw new Error(`/api/ask failed (${askRes.status}): ${errText}`);
    }

    const askData = await askRes.json();
    console.log("   [PASS] AskAgent answered successfully!");
    console.log("   Q:", question);
    console.log("   A:", askData.answer.slice(0, 120) + "...");
    console.log("   Source context:", askData.source_context);

    // 6. Test POST /api/quiz/answer with dynamically generated question
    console.log("\n6. Testing POST /api/quiz/answer with dynamic session question...");
    const firstQ = exp.learning.multiple_choice_questions[0];
    const quizRes = await fetch(`${API_BASE_URL}/api/quiz/answer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: sessionId,
            question_id: firstQ.question_id,
            selected_option: firstQ.correct_option,
        }),
    });

    if (!quizRes.ok) {
        const errText = await quizRes.text();
        throw new Error(`/api/quiz/answer failed (${quizRes.status}): ${errText}`);
    }

    const quizData = await quizRes.json();
    console.log("   [PASS] Quiz answer verified successfully!");
    console.log("   Question  :", firstQ.question);
    console.log("   Selected  :", firstQ.correct_option);
    console.log("   Is Correct:", quizData.is_correct);
    console.log("   Explanation:", quizData.explanation.slice(0, 90) + "...");

    // 7. Test GET /api/session/{sessionId}
    console.log(`\n7. Testing GET /api/session/${sessionId}...`);
    const sessionRes = await fetch(`${API_BASE_URL}/api/session/${sessionId}`);
    if (!sessionRes.ok) throw new Error(`GET /api/session failed: ${sessionRes.status}`);
    const sessionData = await sessionRes.json();
    console.log("   [PASS] Retrieved session data for:", sessionData.session_id);

    console.log("\n==================================================");
    console.log("ALL REAL FRONTEND-TO-BACKEND API CALLS SUCCEEDED!");
    console.log("==================================================");
}

testFullIntegration().catch((err) => {
    console.error("\n[FAIL] Integration test error:", err);
    process.exit(1);
});

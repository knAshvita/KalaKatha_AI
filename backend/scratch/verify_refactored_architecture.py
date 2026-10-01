"""
verify_refactored_architecture.py
══════════════════════════════════════════════════════════════════════════════
Live, unmocked end-to-end verification of the refactored KalaKatha AI backend:
  1. ArtAnalystAgent (single multimodal artwork-understanding specialist)
  2. StorytellerAgent (synthesizes audio tour from understanding)
  3. AskAgent (answers follow-up Q&A and learning prompts from session)
  4. TTSService (Gemini speech generation with persona voice mapping)

NO hardcoded analysis data. NO mocked agent responses.
Runs completely live with Gemini API on a real artwork image.
══════════════════════════════════════════════════════════════════════════════
"""
import sys
import time
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, r"c:\ACM\backend")

from app.main import app
from app.api.artwork import root_agent
import app.api.ask as ask_api_module
from app.services.session_store import session_store


def run_live_verification():
    print("=" * 72)
    print("KALAKATHA AI: LIVE UNMOCKED PIPELINE VERIFICATION")
    print("=" * 72)

    client = TestClient(app)

    # 1. Verify health
    health_res = client.get("/api/health")
    assert health_res.status_code == 200, f"Health check failed: {health_res.text}"
    print(f"[PASS] 1. API Health OK: {health_res.json()}")

    # 2. Verify root_agent structure (NO legacy specialist agent instances)
    print("\n[INFO] Verifying root_agent component structure:")
    assert hasattr(root_agent, "art_analyst"), "root_agent must instantiate ArtAnalystAgent"
    assert hasattr(root_agent, "storyteller_agent"), "root_agent must instantiate StorytellerAgent"
    assert not hasattr(root_agent, "context_agent"), "root_agent must NOT instantiate ContextAgent"
    assert not hasattr(root_agent, "accessibility_agent"), "root_agent must NOT instantiate AccessibilityAgent"
    assert not hasattr(root_agent, "learning_agent"), "root_agent must NOT instantiate LearningAgent"
    assert not hasattr(root_agent, "explore_agent"), "root_agent must NOT instantiate ExploreAgent"
    print("       • root_agent.art_analyst: present")
    print("       • root_agent.storyteller_agent: present")
    print("       • root_agent.context_agent: ABSENT (verified)")
    print("       • root_agent.accessibility_agent: ABSENT (verified)")
    print("       • root_agent.learning_agent: ABSENT (verified)")
    print("       • root_agent.explore_agent: ABSENT (verified)")
    print("[PASS] 2. Verified root_agent contains strictly ArtAnalystAgent and StorytellerAgent")

    # 3. Locate real artwork image
    sample_img_path = Path(r"C:\Users\Alfaz\.gemini\antigravity-ide\brain\875833a7-a719-4943-80f6-6ee0d7c1465a\sample_artwork_1790844258587.jpg")
    assert sample_img_path.exists(), f"Sample artwork image not found at {sample_img_path}"
    img_bytes = sample_img_path.read_bytes()
    print(f"[PASS] 3. Loaded real artwork image ({len(img_bytes)} bytes)")

    # 4. Instrument non-invasive pass-through call spies to verify exact model call counts
    # (These spies do NOT alter or mock any behavior - they pass arguments directly to real methods)
    call_counts = {
        "ArtAnalystAgent": 0,
        "StorytellerAgent": 0,
        "AskAgent": 0,
    }

    orig_art_analyst = root_agent.art_analyst.__class__.analyze
    orig_storyteller = root_agent.storyteller_agent.__class__.generate_story
    orig_answer_question = ask_api_module.answer_question

    async def spy_art_analyst(self, *args, **kwargs):
        call_counts["ArtAnalystAgent"] += 1
        return await orig_art_analyst(self, *args, **kwargs)

    async def spy_storyteller(self, *args, **kwargs):
        call_counts["StorytellerAgent"] += 1
        return await orig_storyteller(self, *args, **kwargs)

    async def spy_ask_agent(*args, **kwargs):
        call_counts["AskAgent"] += 1
        return await orig_answer_question(*args, **kwargs)

    root_agent.art_analyst.__class__.analyze = spy_art_analyst
    root_agent.storyteller_agent.__class__.generate_story = spy_storyteller
    ask_api_module.answer_question = spy_ask_agent

    try:
        # 5. Test live /api/analyze with real image upload
        guide_mode = "storyteller"
        print(f"\n[INFO] Running live POST /api/analyze with guide_mode='{guide_mode}'...")
        t0 = time.time()

        files = {"file": ("renaissance_lady.jpg", img_bytes, "image/jpeg")}
        data = {"guide_mode": guide_mode}

        resp = client.post("/api/analyze", files=files, data=data)
        elapsed = time.time() - t0

        assert resp.status_code == 200, f"/api/analyze failed ({resp.status_code}): {resp.text}"
        result = resp.json()
        session_id = result["session_id"]
        exp = result["experience"]

        print(f"[PASS] 4. /api/analyze completed in {elapsed:.1f}s. Session ID: {session_id}")
        print(f"       Identified Title : {exp['artwork']['title']}")
        print(f"       Identified Artist: {exp['artwork']['artist']}")
        print(f"       Period & Style   : {exp['artwork']['period']} | {exp['artwork']['style']}")
        print(f"       Visual Colors    : {exp['visual_analysis']['colors'][:60]}...")
        print(f"       Visual Focus     : {exp['visual_analysis']['visual_focus']}")
        print(f"       Story Title      : {exp['story']['story_title']}")
        print(f"       Story Chapters   : {len(exp['story']['chapters'])} chapters generated")
        print(f"       Learning Quiz    : {len(exp['learning']['multiple_choice_questions'])} questions generated")
        print(f"       Explore Regions  : {len(exp['explore']['regions'])} hotspot regions generated")
        print(f"       Spatial Center   : {exp['accessibility']['spatial_description']['center']}")

        # 6. Verify model calls during /api/analyze: ArtAnalyst = 1, Storyteller = 1
        print("\n[INFO] Verifying model call counts during /api/analyze:")
        print(f"       ArtAnalystAgent calls : {call_counts['ArtAnalystAgent']}")
        print(f"       StorytellerAgent calls: {call_counts['StorytellerAgent']}")

        assert call_counts["ArtAnalystAgent"] == 1, "ArtAnalystAgent must be called exactly once during /api/analyze"
        assert call_counts["StorytellerAgent"] == 1, "StorytellerAgent must be called exactly once during /api/analyze"
        print("[PASS] 5. Verified: exactly 2 AI model calls made during initial artwork analysis")

        # 7. Verify Session Store
        print("\n[INFO] Verifying session retrieval from SessionStore:")
        session_res = client.get(f"/api/session/{session_id}")
        assert session_res.status_code == 200, f"Session retrieval failed: {session_res.text}"
        session_data = session_res.json()
        assert session_data["session_id"] == session_id
        assert session_data["artwork"]["title"] == exp["artwork"]["title"]
        print(f"[PASS] 6. Session {session_id} successfully retrieved from store")

        # 8. Verify /api/ask using stored context (1 call per question; ArtAnalyst does NOT run)
        print("\n[INFO] Verifying live /api/ask with stored session context:")
        test_questions = [
            "What can I learn from this artwork?",
            "Explain the symbolism of the jewelry and dress",
            "What artistic technique was used?"
        ]

        ask_start_count = call_counts["AskAgent"]
        for idx, q in enumerate(test_questions, start=1):
            time.sleep(2.0)
            analyst_calls_before = call_counts["ArtAnalystAgent"]
            ask_res = client.post("/api/ask", json={"session_id": session_id, "question": q})
            assert ask_res.status_code == 200, f"/api/ask failed for '{q}': {ask_res.text}"
            ask_data = ask_res.json()
            assert len(ask_data["answer"]) > 20

            # Verify ArtAnalyst was NOT called
            assert call_counts["ArtAnalystAgent"] == analyst_calls_before, "ArtAnalyst must not run during /api/ask!"
            # Verify exactly 1 AskAgent call made for this question
            assert call_counts["AskAgent"] == ask_start_count + idx, f"AskAgent should be called exactly once for question {idx}"
            print(f"       Q: '{q}'")
            print(f"       A: {ask_data['answer'][:120]}...\n")

        print(f"[PASS] 7. Verified: AskAgent = 1 per /api/ask ({len(test_questions)} calls), ArtAnalyst calls remained {call_counts['ArtAnalystAgent']}")

        # 9. Verify live TTS audio generation for the chapter (independent service)
        print("[INFO] Verifying independent Gemini TTS audio generation:")
        ch_id = exp["story"]["chapters"][0]["chapter_id"]
        audio_res = client.post("/api/story/audio", json={"session_id": session_id, "chapter_id": ch_id})
        assert audio_res.status_code == 200, f"TTS failed: {audio_res.text}"
        audio_data = audio_res.json()
        assert audio_data["audio_url"].startswith("/audio/")
        assert audio_data["voice"] == "Puck"

        # Verify the generated WAV file is actually readable with RIFF header
        audio_file_res = client.get(audio_data["audio_url"])
        assert audio_file_res.status_code == 200
        assert len(audio_file_res.content) > 1000
        assert audio_file_res.content[:4] == b"RIFF"  # Valid WAV header
        print(f"[PASS] 8. TTS works independently: generated valid WAV ({len(audio_file_res.content)} bytes) served at {audio_data['audio_url']}")

        # 10. Verify /api/quiz/answer using dynamically generated session data (not hardcoded)
        print("\n[INFO] Verifying /api/quiz/answer using dynamically generated session data:")
        first_q = exp["learning"]["multiple_choice_questions"][0]
        correct_opt = first_q["correct_option"]
        wrong_opt = next((opt for opt in first_q["options"] if opt != correct_opt), "Incorrect Option Fallback")

        # Test correct answer
        quiz_res_correct = client.post(
            "/api/quiz/answer",
            json={
                "session_id": session_id,
                "question_id": first_q["question_id"],
                "selected_option": correct_opt
            }
        )
        assert quiz_res_correct.status_code == 200, f"Quiz validation failed: {quiz_res_correct.text}"
        quiz_correct_data = quiz_res_correct.json()
        assert quiz_correct_data["is_correct"] is True, "Expected correct_option to validate as True"

        # Test incorrect answer
        quiz_res_wrong = client.post(
            "/api/quiz/answer",
            json={
                "session_id": session_id,
                "question_id": first_q["question_id"],
                "selected_option": wrong_opt
            }
        )
        assert quiz_res_wrong.status_code == 200, f"Quiz validation failed: {quiz_res_wrong.text}"
        quiz_wrong_data = quiz_res_wrong.json()
        assert quiz_wrong_data["is_correct"] is False, "Expected wrong option to validate as False"

        print(f"       Question   : {first_q['question']}")
        print(f"       Correct Opt: {correct_opt} -> Evaluated as correct: {quiz_correct_data['is_correct']}")
        print(f"       Wrong Opt  : {wrong_opt} -> Evaluated as incorrect: {not quiz_wrong_data['is_correct']}")
        print(f"       Explanation: {quiz_correct_data['explanation'][:100]}...")
        print("[PASS] 9. Quiz validation works dynamically using generated session data")

        print("\n" + "=" * 72)
        print("ALL LIVE UNMOCKED VERIFICATIONS PASSED SUCCESSFULLY!")
        print("=" * 72)

    finally:
        # Restore original methods
        root_agent.art_analyst.__class__.analyze = orig_art_analyst
        root_agent.storyteller_agent.__class__.generate_story = orig_storyteller
        ask_api_module.answer_question = orig_answer_question


if __name__ == "__main__":
    run_live_verification()

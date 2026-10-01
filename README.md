# 🎨 KalaKatha AI — Interactive Digital Museum & Art Experience

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Google ADK](https://img.shields.io/badge/Google%20ADK-Agentic%20AI-4285F4?style=flat&logo=google&logoColor=white)](https://github.com/google/adk)
[![Gemini](https://img.shields.io/badge/Gemini-3.5%20Flash-8E75C2?style=flat&logo=googlegemini&logoColor=white)](https://ai.google.dev)
[![React](https://img.shields.io/badge/React-18.2-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-5.1-646CFF?style=flat&logo=vite&logoColor=white)](https://vitejs.dev)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-3.4-38B2AC?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)

> **KalaKatha AI** is an AI-powered interactive museum and artwork exploration platform. Visitors upload or select an artwork and choose a guide persona. The system produces deep visual analysis, art-historical context, an accessible 8-zone spatial map, an immersive multi-chapter audio tour with voice narration, interactive bounding-box hotspots, grounded Q&A, and dynamic observation quizzes.

---

## 🏛️ System Architecture

KalaKatha AI strictly separates concerns between the **React/Vite presentation layer** and the **Google ADK multi-agent backend**:

```
                              ┌─────────────────────────────────────────┐
                              │      React / Vite Frontend (5173)       │
                              │  - Artwork Viewer & Interactive Hotspots│
                              │  - Multi-Chapter Audio Story Player     │
                              │  - Conversational Docent Q&A Chat       │
                              │  - Dynamic Quiz & Learning Panel        │
                              └────────────────────┬────────────────────┘
                                                   │ HTTP / REST
                                                   ▼
                              ┌─────────────────────────────────────────┐
                              │       FastAPI Backend API (8000)        │
                              │  POST /api/analyze                      │
                              │  POST /api/story/audio                  │
                              │  POST /api/ask                          │
                              │  POST /api/quiz/answer                  │
                              │  GET  /api/session/{id}                 │
                              │  GET  /audio/{filename}                 │
                              └────────────────────┬────────────────────┘
                                                   │
                ┌──────────────────────────────────┴──────────────────────────────────┐
                ▼                                                                     ▼
      [INITIAL ANALYSIS PIPELINE]                                           [ON-DEMAND SERVICES]
               Artwork Image                                                 Session ID + Query
                    │                                                                 │
                    ▼                                                                 ├───────────────┐
       ┌─────────────────────────┐                                                    ▼               ▼
       │    ArtAnalystAgent      │                                           ┌─────────────────┐ ┌───────────────┐
       │ (1 Multimodal pass)     │                                           │    AskAgent     │ │  TTSService   │
       └────────────┬────────────┘                                           │ (1 model call/q)│ │ (Gemini TTS)  │
                    │ ArtworkUnderstanding                                   └─────────────────┘ └───────┬───────┘
                    ▼                                                                                    ▼
       ┌─────────────────────────┐                                                                   WAV Speech
       │    StorytellerAgent     │
       │ (1 Synthesis pass)      │
       └────────────┬────────────┘
                    │
                    ▼
          ┌───────────────────┐
          │   Session Store   │
          │(In-Memory Storage)│
          └───────────────────┘
```

---

## 🤖 The 3 Specialist Agents & 1 Dedicated Service

The backend utilizes **exactly 3 Google ADK AI agents** and **1 dedicated TTS audio service**:

| Agent / Service | Technology | Role | Execution Timing |
|---|---|---|---|
| **ArtAnalystAgent** | Google ADK (`LlmAgent`) + Gemini Multimodal | Single multimodal pass: visual observations, artwork identification (with epistemic uncertainty), art history, symbolism, techniques, and 8-zone spatial accessibility layout. | Runs **once** during `/api/analyze`. |
| **StorytellerAgent** | Google ADK (`LlmAgent`) + Gemini | Synthesizes `ArtworkUnderstanding` into an immersive 4–6 chapter museum tour tailored to the selected persona. | Runs **once** during `/api/analyze`. |
| **AskAgent** | Google ADK (`LlmAgent`) + Gemini | Answers visitor questions grounded strictly in stored session data and past conversation turns. Strictly never re-invokes vision. | Runs **on demand** during `/api/ask`. |
| **TTSService** | Gemini Speech TTS (`Client.models.generate_content`) | Synthesizes high-fidelity WAV speech for each story chapter with persona-matched voices. | Runs **on demand** during `/api/story/audio`. |

> **Single Source of Truth (`ArtworkUnderstanding`)**:
> All client-facing analytical dimensions (visual analysis, historical context, accessibility, educational concepts, dynamic quizzes, and explore hotspots) are derived deterministically from `ArtworkUnderstanding` without redundant Gemini calls.

---

## 🎭 Guide Personas & Voice Profiles

Visitors can tailor their experience by selecting one of four personas:

| Persona | Voice | Tone & Character | Best For |
|---|---|---|---|
| **Storyteller** | `Puck` | Rich narrative cadence, evocative storytelling grounded in historical facts. | Immersive museum visitor experience. |
| **Professor** | `Charon` | Academic precision, curatorial depth, art-historical terminology, provenance. | Students, researchers, and art historians. |
| **Friendly** | `Aoede` | Warm, conversational enthusiasm; explains complex concepts simply. | Casual museum visitors, families, and youth. |
| **Accessibility**| `Leda` | Spatial arrangement, tactile textures, audio-described sensory navigation. | Visually impaired visitors and screen-reader users. |

---

## ✨ Application Features

### 1. Landing & Artwork Ingestion
- Clean drag-and-drop artwork uploader with instant client-side preview.
- Image validation (JPEG, PNG, WebP, GIF, BMP, TIFF; up to 10MB).
- Pre-curated classic artwork quick-selection.
- Persona selection cards with distinct visual indicators.

### 2. Interactive Artwork Viewer & Hotspots
- Normalized bounding-box hotspots rendered over the artwork from real backend coordinates (`experience.explore.regions`).
- Click-to-inspect highlights with descriptions and focal importance badges.
- Dominant color palette swatches extracted and visualized dynamically.

### 3. Multi-Chapter Museum Audio Tour (Story)
- 4 to 6 progressive chapters: *The First Gaze*, *The Journey*, *The Lasting Impression*.
- High-fidelity Gemini TTS audio narration served directly from `/audio/*.wav`.
- Synchronized playback controls: Play, Pause, Seek bar, Elapsed/Duration timers, and focal zoom.

### 4. Conversational Docent Q&A (Ask)
- Real-time conversation interface with `AskAgent`.
- Multi-turn conversation history maintained in the backend session.
- Grounding badges (`source_context`) indicating whether answers drew from Visual, Context, or Story data.

### 5. Educational Insights & Dynamic Quiz (Learn)
- Core artistic concepts, techniques, and intriguing verifiable facts.
- 3 dynamic multiple-choice quiz questions generated per artwork.
- Instant server-side evaluation via `POST /api/quiz/answer` with immediate feedback and curatorial explanations.

### 6. Curatorial Deep-Dive & Accessibility (Explore)
- 8-zone spatial breakdown (Foreground, Center, Background, Left, Right, etc.).
- Audio description script compliant with museum accessibility standards.
- Epistemic uncertainty indicators (confidence levels, provenance notes).

---

## 📁 Repository Structure

```
ACM/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application, CORS, static routes
│   │   ├── config.py               # Settings & multi-key API rotation pool
│   │   ├── agent.py                # Facade interface
│   │   ├── schemas/
│   │   │   └── artwork.py          # Pydantic models (ArtworkUnderstanding, Experience, etc.)
│   │   ├── agents/
│   │   │   ├── root_agent.py       # KalaKathaRootAgent orchestrator (Stages 1 & 2)
│   │   │   ├── art_analyst.py      # Unified multimodal artwork understanding agent
│   │   │   ├── storyteller_agent.py# Multi-chapter museum tour synthesis agent
│   │   │   ├── ask_agent.py        # Conversational Q&A docent agent
│   │   │   ├── adk_runner.py       # ADK runner bridge with automatic key rotation
│   │   │   └── base.py             # Common base agent
│   │   ├── services/
│   │   │   ├── tts_service.py      # Gemini TTS speech generation & WAV caching
│   │   │   ├── session_store.py    # In-memory session & turn storage
│   │   │   └── quiz_service.py     # Quiz answer verification & scoring
│   │   └── api/
│   │       ├── artwork.py          # POST /api/analyze
│   │       ├── ask.py              # POST /api/ask
│   │       ├── story_audio.py      # POST /api/story/audio
│   │       ├── quiz.py             # POST /api/quiz/answer
│   │       ├── session_api.py      # GET  /api/session/{id}
│   │       └── health.py           # GET  /api/health
│   ├── audio_cache/                # Generated WAV files served at /audio/
│   ├── tests/                      # Automated test suite (65 passing unit tests)
│   ├── requirements.txt            # Python dependencies
│   └── .env.example                # Backend environment variables template
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── kalakathaApi.js     # Unified API client (clean fetch layer)
│   │   ├── components/
│   │   │   ├── ArtworkViewer.jsx   # Artwork canvas & interactive hotspot overlay
│   │   │   ├── ListenTab.jsx       # Multi-chapter audio player & TTS controller
│   │   │   ├── AskTab.jsx          # Conversational docent chat interface
│   │   │   ├── LearnTab.jsx        # Learning concepts & dynamic MCQ quiz
│   │   │   ├── ExploreTab.jsx      # Spatial zones, facts, and accessibility details
│   │   │   └── Navbar.jsx          # App navigation header
│   │   ├── App.jsx                 # Master application view & session coordinator
│   │   ├── index.css               # Tailwind CSS & custom design system styling
│   │   └── main.jsx                # React root mount
│   ├── public/                     # Static assets
│   ├── package.json                # Frontend dependencies & scripts
│   ├── vite.config.js              # Vite bundler configuration
│   ├── tailwind.config.js          # Tailwind CSS styling configuration
│   ├── .env.example                # Frontend environment template
│   └── test_api_client.js          # End-to-end API client verification test
│
└── README.md                       # Comprehensive project documentation
```

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** & npm
- A **Gemini API Key** from [Google AI Studio](https://aistudio.google.com/)

---

### Step 1: Set Up and Start the Backend

1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   ```bash
   # Windows (PowerShell / Command Prompt)
   python -m venv .venv
   .venv\Scripts\activate

   # macOS / Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create your `.env` configuration file:
   ```bash
   # Copy template
   cp .env.example .env
   ```
   Edit `.env` and set your key:
   ```ini
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   GEMINI_MODEL=gemini-3.5-flash
   CORS_ORIGINS=http://localhost:5173,http://localhost:5174,http://127.0.0.1:5173,http://127.0.0.1:5174
   ```

5. Launch the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   - API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Health Status: [http://localhost:8000/api/health](http://localhost:8000/api/health)

---

### Step 2: Set Up and Start the Frontend

1. Open a new terminal and navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```

2. Install npm dependencies:
   ```bash
   npm install
   ```

3. Configure your frontend environment:
   ```bash
   # Copy template
   cp .env.example .env
   ```
   Ensure `.env` contains:
   ```ini
   VITE_API_BASE_URL=http://localhost:8000
   ```
   *(Note: Never place secret API keys in the frontend!)*

4. Start the Vite development server:
   ```bash
   npm run dev
   ```

5. Open your browser and navigate to:
   **[http://localhost:5173](http://localhost:5173)**

---

## 📡 Backend API Reference

### 1. `POST /api/analyze`
Analyzes an uploaded artwork image using the 2-stage sequential pipeline (`ArtAnalystAgent` → `StorytellerAgent`).

- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `file` *(required)*: Artwork image binary (JPEG/PNG/WebP).
  - `guide_mode` *(optional)*: `storyteller` | `professor` | `friendly` | `accessibility` (default: `storyteller`).
- **Response**:
  ```json
  {
    "status": "completed",
    "session_id": "kk_c2c3e7c9851d",
    "experience": {
      "artwork": {
        "title": "Girl with a Pearl Earring",
        "artist": "Johannes Vermeer",
        "period": "Dutch Golden Age",
        "style": "Baroque Tronie"
      },
      "visual_analysis": {
        "visual_focus": "The pearl earring and luminous eyes...",
        "colors": "Deep ochre, ultramarine blue, soft cream...",
        "composition": "Three-quarter turn portrait..."
      },
      "story": {
        "story_title": "Light in the Dark",
        "chapters": [
          {
            "chapter_id": "chapter_1",
            "title": "The First Gaze",
            "narration": "Step forward into the quiet darkness...",
            "estimated_duration_seconds": 30
          }
        ]
      },
      "learning": {
        "key_concepts": ["Chiaroscuro", "Ultramarine Pigment"],
        "multiple_choice_questions": [
          {
            "question_id": "q1",
            "question": "What is the primary visual focus of this artwork?",
            "options": ["The pearl earring", "The background curtain", "A gold frame", "The signature"],
            "correct_option": "The pearl earring",
            "explanation": "Vermeer directs illumination toward the drop-pearl earring."
          }
        ]
      },
      "explore": {
        "regions": [
          {
            "region_id": "region_focus",
            "label": "The Pearl Earring",
            "description": "A single stroke of lead-white pigment creating luminescence.",
            "position": { "x": 0.35, "y": 0.42, "width": 0.20, "height": 0.25 }
          }
        ]
      }
    }
  }
  ```

---

### 2. `POST /api/story/audio`
Generates persona-matched voice narration for a given chapter using Gemini TTS.

- **Method**: `POST`
- **Body**:
  ```json
  {
    "session_id": "kk_c2c3e7c9851d",
    "chapter_id": "chapter_1"
  }
  ```
- **Response**:
  ```json
  {
    "session_id": "kk_c2c3e7c9851d",
    "chapter_id": "chapter_1",
    "chapter_title": "The First Gaze",
    "audio_url": "/audio/a77fa200d3054a1b8bcb94097464c1bc.wav",
    "voice": "Puck",
    "duration_hint_seconds": 30
  }
  ```

---

### 3. `POST /api/ask`
Interacts with the `AskAgent` for grounded artwork Q&A without re-invoking vision.

- **Method**: `POST`
- **Body**:
  ```json
  {
    "session_id": "kk_c2c3e7c9851d",
    "question": "What pigment was used for the blue turban?"
  }
  ```
- **Response**:
  ```json
  {
    "session_id": "kk_c2c3e7c9851d",
    "question": "What pigment was used for the blue turban?",
    "answer": "Vermeer famously utilized natural ultramarine, an extraordinarily expensive pigment ground from lapis lazuli imported from Afghanistan...",
    "source_context": ["VisualAnalysis", "ContextAnalysis"]
  }
  ```

---

### 4. `POST /api/quiz/answer`
Dynamically evaluates a user's quiz submission against session context.

- **Method**: `POST`
- **Body**:
  ```json
  {
    "session_id": "kk_c2c3e7c9851d",
    "question_id": "q1",
    "selected_option": "The pearl earring"
  }
  ```
- **Response**:
  ```json
  {
    "session_id": "kk_c2c3e7c9851d",
    "question_id": "q1",
    "selected_option": "The pearl earring",
    "is_correct": true,
    "correct_option": "The pearl earring",
    "explanation": "Vermeer directs illumination toward the drop-pearl earring."
  }
  ```

---

### 5. `GET /api/session/{session_id}`
Retrieves the complete cached `KalaKathaExperience` object to restore state on page reloads.

---

### 6. `GET /api/health`
Checks backend liveness and confirms Gemini API key readiness.

---

## 🧪 Testing & Verification

### 1. Automated Unit Tests (Backend)
Run the 65 unit tests covering schemas, routing, sessions, agents, and TTS:
```bash
cd backend
pytest tests/ -v -m "not integration"
```
**Result**: 65 passed in 0.9s.

### 2. Live Unmocked Integration Test
Run the end-to-end integration script verifying the live pipeline against Gemini:
```bash
cd frontend
node test_api_client.js
```
**Verified Results**:
- `GET /api/health` → `status: ok, gemini_api_key_set: true`
- `POST /api/analyze` → Real image analyzed in ~34s, session initialized with 5 chapters, 3 questions, 3 hotspots.
- `POST /api/story/audio` → Real Gemini TTS synthesized 2.3MB WAV audio with voice `Puck`.
- `POST /api/ask` → AskAgent answered with multi-turn grounding context.
- `POST /api/quiz/answer` → Dynamic quiz answer scored and verified.
- `GET /api/session/{id}` → Session successfully restored.

---

## 🔒 Security Best Practices

- **Zero Client Credentials**: No Gemini API keys or backend tokens are exposed to the browser.
- **Configurable Backend Target**: Frontend strictly communicates via `VITE_API_BASE_URL`.
- **CORS Protection**: Configured via FastAPI middleware supporting explicit origins without wildcard credentials.
- **Multi-Key Failover**: Backend supports comma-separated `GEMINI_API_KEYS` with automatic transparent key rotation on HTTP 429 quota exhaustion.

---

## 👥 Contributors & Hackathon Team

- **KalaKatha AI Development Team**
- Built for the **ACM AI Hackathon**

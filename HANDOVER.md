# MindGuard: Comprehensive System Design & Project Handover Document

## 1. Executive Summary
**MindGuard** is a full-stack, multimodal AI platform built to detect and triage mental health crises in real-time. Unlike standard LLMs (e.g., ChatGPT) which struggle with Code-Mixed Dravidian languages, MindGuard is specifically engineered to understand **Tanglish** (Tamil written in English script). 

The primary objective is to prevent **False Positives** (triggering suicide interventions for benign slang like *"suicide panna mattan"*) and **False Negatives** (missing disguised cries for help) by utilizing an advanced 8-Layer Hybrid Detection Ensemble and Google's MuRIL transformer, fine-tuned via LoRA.

---

## 2. System Architecture Overview
The system is divided into three distinct operational domains:
1. **The Client (Frontend):** A responsive React application providing the chat interface and the emergency UI override.
2. **The Server (Backend):** A FastAPI Python server handling HTTP requests, database transactions, and audio-processing (via Whisper).
3. **The Engine (AI/ML):** The 8-layer NLP pipeline responsible for analyzing user text and returning a deterministic severity classification.

---

## 3. The 8-Layer AI Pipeline (Deep Dive)
The core intelligence resides in `backend/app/services/detection/ensemble.py`. Every user message is processed sequentially:

* **Layer 1 (Input Gate):** Sanitizes the text by scrubbing PII (phone numbers, URLs, emails), detects and blocks prompt injections, and validates the script type. It rejects pure Unicode Tamil, forcing the system to focus on Romanized Tanglish.
* **Layer 2 (Chunking Engine):** Splits long paragraphs into individual sentences. This prevents a single severe sentence from being mathematically diluted by surrounding benign text.
* **Layer 3 (Context Analyzer):** A linguistic parser that extracts critical metadata:
  * **Subject Extraction:** Is the text self-referential (*"I"*) or about someone else (*"My friend"* / *"Movie"*).
  * **Tone Detection:** Flags sarcasm, hyperbole, and explicit negations (e.g., *"illa"*, *"maaten"*).
* **Layer 4 (Phonetic Tanglish Translator):** A custom dictionary that normalizes hundreds of phonetic Tanglish spellings (e.g., *santhosam, kashtama*) into standard English tokens to bridge the gap for legacy models.
* **Layer 5 (Lexicon Agent):** O(1) exact-match phrase detection for acute clinical keywords.
* **Layer 6 (Sentiment Agent):** Utilizes NLTK's VADER model, specifically adapted for the output of the Phonetic Translator, to assign a continuous polarity score.
* **Layer 7 (Embedding kNN Agent):** Vectorizes the text and plots it in a multi-dimensional space. It computes the cosine similarity against a curated anchor bank of 67 labeled severe/moderate sentences.
* **Layer 8 (The Aggregator):** A mathematical consensus engine. 
  * *Constraint:* A classification of `Severe` strictly requires positive signals from $\ge 2$ independent agents *AND* zero negation flags from Layer 3. 
  * *Override:* If Layer 3 detects negation (e.g., *"I do NOT want to die"*), the aggregator artificially caps the severity, solving the NLP false-positive crisis loop.

---

## 4. Machine Learning & Model Fine-Tuning
Beyond the deterministic 8-layer pipeline, the project incorporates cutting-edge Deep Learning for natural language representation.

* **Base Model:** `google/muril-base-cased` (236M parameters), trained on 17 Indian languages.
* **Dataset:** 185,973 rows of raw Tanglish corpus (`vishnu-n/Tanglish-Corpus-185k`).
* **Technique (PEFT/LoRA):** Instead of full parameter tuning, the project uses **Low-Rank Adaptation (LoRA)** on the `query` and `value` self-attention matrices ($r=8, \alpha=16, dropout=0.1$). This reduces trainable parameters to **0.12%** ($294,912$ parameters).
* **Objective:** Masked Language Modeling (MLM). The script (`scripts/finetune_muril.py`) masks 15% of the Tanglish words and forces the AI to predict them, teaching the model Tanglish syntax and slang natively without requiring manual translations.

---

## 5. Database Schema (Data Models)
The backend utilizes SQLAlchemy over a SQLite database. 

* **Users / Sessions:** Tracks anonymous or authenticated user sessions.
* **Chats:** Stores the conversation history, timestamp, and the user/bot role.
* **Indicators (`indicator.py`):** Stores Multimodal exploratory metrics extracted from the user:
  * *Speech Metrics:* Words per minute (WPM), pause ratio, mean pause length, pitch variance (extracted via OpenAI Whisper).
  * *Linguistic Metrics:* Code-Mixing Index (CMI), switch-point frequency, Tamil-to-Roman ratio.
* **Alerts (`alert.py`):** Logs every instance where the Aggregator triggers a `Severe` event, storing the raw text, the confidence score, and the specific agents that voted for the alert.

---

## 6. Frontend Architecture & Crisis UI
**Tech Stack:** React (Vite) + TailwindCSS.
The frontend emphasizes a modern, calming aesthetic (glassmorphism, soft gradients, dynamic micro-animations) to reduce user anxiety.

**The Crisis Intervention Protocol (`AnalyzePage.jsx`):**
When the user sends a message, the frontend awaits the JSON response from the `/analyze` backend endpoint. 
* If the payload returns `predicted_class === 'Severe'` and `confidence >= 40%`, the standard chat UI is immediately suspended.
* The frontend renders an un-closable **Crisis Mode** screen, displaying emergency helpline numbers and supportive resources, prioritizing human safety over conversational continuity.

---

## 7. API Endpoints
* `POST /api/v1/analyze`: The core endpoint. Accepts `{ "text": "...", "session_id": "..." }`. Returns the final severity label, confidence score, and detailed evidence logs from the 8-layer aggregator.
* `POST /api/v1/chat`: Handles standard conversational flow when the text is marked `Normal` or `Mild`.
* `POST /api/v1/voice`: Accepts `.wav` or `.mp3` uploads. Pipes the audio through Whisper ASR, generates transcripts, calculates acoustic biomarkers (pause ratio, WPM), and forwards the transcript to `/analyze`.

---

## 8. Testing Methodology & Performance
The project includes a highly adversarial testing suite (`test_analyze.py`) containing 35 edge-case inputs designed to break clinical chatbots.
* **Categories Tested:** Positive English, Positive Tanglish, Negated Severe Tanglish, Mild Stress, Moderate Depression, Severe Crisis, and Out-of-Scope (Emojis/Gibberish).
* **Performance:** Do not use the earlier 91% accuracy claim. The current heuristic implementation was re-evaluated on the repository's small internal test split at 0.78 macro-F1 and 0.83 severe recall after safety fixes. This is not clinical validation; see `docs/production-readiness.md` before making product or medical-performance claims.

---

## 9. Setup & Installation Instructions

**Prerequisites:** Python 3.10+, Node.js 18+.

**Step 1: Start Backend**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Step 2: Start Frontend**
```bash
cd frontend
npm install
npm run dev
```

**Step 3: Run the ML Fine-Tuning (Optional)**
```bash
cd backend
python scripts/download_dataset.py
python scripts/finetune_muril.py
```

---

## 10. Future Work & Exploratory Features
Future iterations of MindGuard will fully integrate the `ExploratoryIndicator` models, fusing the Tanglish Text Ensemble with real-time acoustic analysis. By analyzing voice jitter, shimmer, and pause ratios directly from the `/voice` endpoint, the system will be able to detect clinical psychomotor retardation, offering a truly 360-degree multimodal crisis detection engine.

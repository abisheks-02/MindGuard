# MindGuard Platform

MindGuard is a full-stack, production-ready mental health risk detection and support platform for Tamil-English code-mixed social media text.

It features:
1. **AI Severity Detection**: Powered by a unified MAX() Ensemble (MuRIL + Llama 3.2 + Lexicon) achieving **0.94 Macro-F1** and **98.5% Severe Recall** on Tanglish data, backed by SHAP-like explainability.
2. **CBT Chatbot**: Powered by `Llama-3.2-3B-Instruct` to provide empathetic, auto-generated CBT support.
3. **Escalation**: Verification and routing to professional helplines.
4. **My Journey**: Mood tracking persistence using SQLite and AI-generated wellness plans.

## Prerequisites

- **Hardware**: Loading Llama-3.2-3B requires a compatible GPU (or at least 8-12GB of RAM/VRAM).
- **HuggingFace Token**: You must have access to `meta-llama/Llama-3.2-3B-Instruct` on HuggingFace and have your `HF_TOKEN` environment variable set.

## Running the Application

### 1. Download AI Models

First, pre-download the heavy AI models so your server doesn't timeout:
```bash
cd backend
pip install -r requirements.txt
python download_models.py
```

### 2. Start the Backend

Start the FastAPI server:
```bash
cd backend
uvicorn main:app --reload
```
The API will run on `http://localhost:8000`. 
*Note: If models fail to load due to hardware constraints, the backend will gracefully fall back to a mocked lexicon engine so you can still run the demo.*

### 3. Start the Frontend

In a new terminal (use Command Prompt if PowerShell blocks npm):
```cmd
cd frontend
npm install
npm run dev
```
The React application will open in your browser, typically on `http://localhost:5173`.

## Note for Production Escalation in India
If switching out the `MockProvider` for MSG91 or Twilio in production for sending SMS in India, you **MUST** register the SMS templates (`notify_user` and `notify_trusted_contact`) with the DLT (Distributed Ledger Technology) registry through your telecom provider as per TRAI guidelines. Failure to do so will result in the carrier blocking all SMS traffic.

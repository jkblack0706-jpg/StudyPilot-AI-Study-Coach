# StudyPilot — AI Study Coach

**Project #1 — Web App with an AI Agent** · Jalen Black

**Public app:** https://studypilot-ai-coach.onrender.com  
**Source:** https://github.com/jkblack0706-jpg/StudyPilot-AI-Study-Coach

A responsive Python/FastAPI web application coordinating four distinct, sequential agents:

1. **Planner** — produces a time-boxed study plan.
2. **Tutor** — develops a concise lesson from the plan.
3. **Quiz Maker** — generates three structured quiz questions and answers.
4. **Reviewer** — reviews the study materials and flags study gaps.

There are two clearly differentiated modes:
- **Offline demo:** deterministic templates, no API key necessary; demonstrates the interface and workflow.
- **Live Gemini AI:** four sequential Gemini model calls, requires an available model, quota and a server-side `GEMINI_API_KEY`.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```

Open http://127.0.0.1:8000/ and select **Offline demo** to try without a key.

## Run with live Gemini AI

Set `GEMINI_API_KEY` as a server-side environment variable, not in source code or in the browser. Optionally set `GEMINI_MODEL` (default `gemini-3-flash`; use a model enabled for your API project). For the Render service, open **Environment** in the Render dashboard and add `GEMINI_API_KEY` there. Do not commit secrets. AI mode may be unavailable due to provider quota or model availability.

## Render deployment

The service is configured to build with `pip install -r requirements.txt` and start with:

```bash
uvicorn app:app --host 0.0.0.0 --port $PORT
```

Render deploy URL: https://studypilot-ai-coach.onrender.com

Health endpoint: https://studypilot-ai-coach.onrender.com/health

## API

`POST /api/study`:
```json
{"topic":"SQL joins","goal":"Prepare for an exam","level":"Intermediate","minutes":30,"mode":"demo"}
```

Returns the plan, lesson, quiz, review and agent trace. Inputs are validated and provider errors are reported without mislabeling demo output as live AI.

## Security and attribution

No API keys belong in the public repository; `.gitignore` excludes `.env`. This is a course demonstration and not a production service (no accounts, rate limiting or persistent storage). Generated advice may contain errors and should be checked against course materials.

Prepared for Jalen Black with AI assistance. Review and disclose assistance as required by the instructor.

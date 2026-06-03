# Codesense

Codesense is an AI-powered developer assistant for analyzing repositories, generating architecture diagrams, and answering codebase questions through a chatbot.

## Features

- Ingest GitHub repositories and store source code as searchable vectors
- Generate repository summaries, setup guides, architecture diagrams, workflow flowcharts, and ER diagrams
- Chat with the repository using AI-powered contextual search
- Track user projects, credits, and conversation history

## Repository structure

- `client/` — React + Vite frontend
- `server/` — FastAPI backend and ingestion/chat services

## Requirements

- Node.js 20+ and npm
- Python 3.12+ with a virtual environment
- MongoDB instance accessible from the server
- `git` installed locally for repository ingestion
- Google Gemini API key for AI features

## Setup

### Server

1. Open a terminal in `server/`
2. Create and activate the Python environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

4. Copy the example env file and fill in values:

```powershell
copy .env.example .env
```

5. Start the API server:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Client

1. Open a second terminal in `client/`
2. Install dependencies:

```powershell
npm install
```

3. Start the Vite development server:

```powershell
npm run dev
```

4. Open the client in the browser at `http://localhost:5173`

## Environment variables

Create `server/.env` using `server/.env.example` with values for:

- `MONGO_URI`
- `DATABASE_NAME`
- `GEMINI_API_KEY`
- `GEMINI_MODEL_NAME`
- `SECRET_KEY`
- `ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `MONTHLY_FREE_CREDITS`
- `PORT`
- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`

## Notes

- The server exposes a health endpoint at `/health`
- The frontend uses `http://localhost:8000` for API requests by default
- Ingestion uses `git clone` and may take several minutes for large repositories


# Codesense Server

The backend powers ingestion, analysis, search, and chat.

## Requirements

- Python 3.12+
- Virtual environment in `server/.venv`
- MongoDB accessible from the server
- `git` installed locally
- Google Gemini API key

## Setup

1. Open a terminal in `server/`
2. Create and activate the virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

4. Copy the example environment file:

```powershell
copy .env.example .env
```

5. Fill in values in `server/.env`

## Run

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API

- `GET /health` — health check
- `POST /auth/register` — register a user
- `POST /auth/login` — login and receive token
- `GET /profile/me` — fetch authenticated profile
- `POST /project` — create a project (requires user_id)
- `GET /project/user/{user_id}` — list projects for a user
- `GET /project/{project_id}/repository` — repository details
- `GET /chat/{project_id}` — retrieve chat history for a project
- `POST /chat/{conversation_id}/message?repo_id={repo_id}` — send a chat question

## Notes

- The ingestion pipeline stores repository chunks in MongoDB with repo metadata.
- Chat queries use vector search filtered by the project repository id.
- The server starts the MongoDB connection during FastAPI startup and closes it on shutdown.

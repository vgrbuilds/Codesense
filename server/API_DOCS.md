# Codesense Server API Docs

This document is for client developers integrating with the Codesense backend.

## Base URL

- Local: `http://localhost:8000`
- Production: `https://<your-render-service>.onrender.com`

## Auth Model

- Auth type: `Bearer` JWT
- Login endpoint expects `application/x-www-form-urlencoded` data.
- Protected endpoints require:

`Authorization: Bearer <access_token>`

## Health Endpoints

### `GET /health`
- Purpose: liveness check
- Auth: none
- Response:
```json
{
  "success": true,
  "status": "ok"
}
```

### `GET /ready`
- Purpose: readiness check (Mongo connectivity)
- Auth: none

## Authentication

### `POST /auth/register`
- Auth: none
- Body (JSON):
```json
{
  "email": "dev@example.com",
  "username": "devuser",
  "password": "secret123"
}
```
- Success response:
```json
{
  "success": true,
  "message": "User registered successfully",
  "user_id": "682ddc...",
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

### `POST /auth/login`
- Auth: none
- Content-Type: `application/x-www-form-urlencoded`
- Fields:
  - `username`: user email
  - `password`: user password
- Success response:
```json
{
  "success": true,
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

## Users

### `GET /users/{user_id}`
- Auth: required
- Owner-only route

### `PATCH /users/{user_id}`
- Auth: required
- Owner-only route
- Body (JSON, partial):
```json
{
  "username": "new_name",
  "email": "new@example.com",
  "new_password": "newpass123",
  "avatar": "https://..."
}
```

### `DELETE /users/{user_id}`
- Auth: required
- Owner-only route

## Repositories

### `POST /repositories/ingest`
- Auth: none
- Purpose: ingest repo, chunk code, generate artifacts, upload media/docs to Cloudinary.
- Body (JSON):
```json
{
  "source_path": "",
  "url": "https://github.com/owner/repo",
  "assets": [],
  "summary": null,
  "documentation": [],
  "design": null
}
```
- Notes:
  - If `source_path` is empty, backend fetches from `url`.
  - If repo was already ingested (same normalized URL), backend reuses existing repository (`reused: true`) and skips re-scrape.
- Success response (new ingestion):
```json
{
  "success": true,
  "repository_id": "682ddf...",
  "files_scanned": 83,
  "chunks_created": 612,
  "assets_uploaded": 9,
  "documents_uploaded": 2
}
```
- Success response (reused):
```json
{
  "success": true,
  "repository_id": "682ddf...",
  "files_scanned": 0,
  "chunks_created": 0,
  "assets_uploaded": 0,
  "documents_uploaded": 0,
  "reused": true
}
```

### `GET /repositories/{repository_id}`
- Auth: none
- Returns repository record (summary, docs, design, assets)

### `POST /repositories`
- Auth: none
- Creates a repository record directly (usually not needed if using `/repositories/ingest`)

## Projects

### `POST /projects`
- Auth: required
- Body (JSON):
```json
{
  "name": "Capstone",
  "description": "Code understanding workspace",
  "repository_url": "https://github.com/owner/repo"
}
```
- Business logic:
  - 2 credits consumed per project creation.
  - Credits reset to 10 every 30 days.
  - Repository ingestion is reused by URL when available.
- Success response:
```json
{
  "success": true,
  "message": "Project created successfully",
  "project_id": "682de1...",
  "repository_id": "682ddf...",
  "credits_remaining": 8
}
```

### `GET /projects`
- Auth: required
- Returns current user projects

### `GET /projects/{project_id}`
- Auth: required
- Owner-check enforced

### `DELETE /projects/{project_id}`
- Auth: required
- Owner-check enforced

## Chunks

### `GET /chunks/repository/{repository_id}`
- Auth: none
- Returns chunks for a repository

### `GET /chunks/{chunk_id}`
- Auth: none

### `POST /chunks`
- Auth: none
- Manual chunk creation endpoint (mostly internal/testing)

## Messages and RAG Query

### `POST /messages`
- Auth: required
- Body (JSON):
```json
{
  "conversation_id": "conv_001",
  "role": "user",
  "content": "Explain this file",
  "references": []
}
```

### `POST /messages/query`
- Auth: required
- Purpose: ask a code question with RAG over repository chunks.
- Body (JSON):
```json
{
  "conversation_id": "conv_001",
  "repository_id": "682ddf...",
  "question": "How is auth token validation done?",
  "top_k": 5
}
```
- Success response:
```json
{
  "success": true,
  "answer": "....",
  "references": [
    {
      "chunk_id": "682de3...",
      "file_path": "src/core/security.py",
      "start_line": 28,
      "end_line": 55,
      "score": 0.832114
    }
  ],
  "retrieved_chunks": 5
}
```

## Recommended Client Flow

1. Register/Login and store JWT.
2. Create project with repo URL (`POST /projects`).
3. Read returned `repository_id`.
4. Use `POST /messages/query` with `repository_id` for chat.
5. Render `references` as clickable file+line citations in UI.

## Error Shape

Service errors typically return:
```json
{
  "success": false,
  "message": "Some error message"
}
```

## CORS

CORS is currently open to all origins/methods/headers in backend configuration.

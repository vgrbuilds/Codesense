## API Design

The server exposes a REST API built with FastAPI and MongoDB. Authentication uses OAuth2 password flow with JWT bearer tokens. Protected routes depend on `get_current_user` and validate the token before allowing access.

# Endpoints

/auth/register
    POST: register a new user with `email`, `username`, and `password`.

/auth/login
    POST: obtain a bearer token using `email` and `password`.

/users/{user_id}
    GET: retrieve the authenticated user profile.
    PATCH: update user fields such as `username`, `email`, `avatar`, or password.
    DELETE: delete the authenticated user account.

/projects
    POST: create a new project for the authenticated user.
    Business rules:
        - 2 credits are consumed per project creation.
        - credits reset to 10 every 30 days.
        - repository ingestion is reused when URL already exists (no re-scrape).
    GET: list projects owned by the authenticated user.

/projects/{project_id}
    GET: read a specific project by ID.
    DELETE: delete a specific project if owned by the authenticated user.

/repositories
    POST: create a new repository record.

/repositories/{repository_id}
    GET: retrieve a repository by ID.

/repositories/ingest
    POST: ingest a repository by `url` (or `source_path`) and persist chunks + artifacts.
    Auth: not required.
    Response includes: `repository_id`, `files_scanned`, `chunks_created`, `assets_uploaded`, `documents_uploaded`.

/chunks
    POST: create a new code chunk with embedding and repository reference.

/chunks/{chunk_id}
    GET: retrieve a chunk by ID.

/chunks/repository/{repository_id}
    GET: list chunks for a specific repository.

/messages
    POST: create a chat/message record for the authenticated user.
    POST /messages/query: run RAG query against ingested repository chunks.

/health
    GET: liveness check.

/ready
    GET: readiness check (includes Mongo ping).

## DB Design

The server uses MongoDB collections to store users, projects, repositories, chunks, and messages. Each collection is managed through the central `MongoDB` class in `src/db/mongo.py`, and the database name is read from `DATABASE_NAME`.

# 1. Collections

users {
    _id,
    email,
    username,
    hashed_password,
    avatar,
    credits,
    created_at,
}

projects {
    _id,
    name,
    description,
    owner_id,
    repository_url,
    created_at,
}

repositories {
    _id,
    url,
    assets,
    summary,
    documentation,
    design,
    created_at,
}

chunks {
    _id,
    repository_id,
    file_path,
    content,
    chunk_index,
    embedding,
    language,
    start_line,
    end_line,
    created_at,
}

messages {
    _id,
    conversation_id,
    user_id,
    role,
    content,
    references,
    created_at,
}

## Configuration

Environment variables are loaded from `.env` via `src/core/config.py`.

Required variables:

- `MONGO_URI`
- `DATABASE_NAME`
- `SECRET_KEY`
- `ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`

Optional / additional variables:

- `PORT`
- `GEMINI_KEY`
- `GITHUB_TOKEN`
- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`

## Ingestion Notes

`POST /repositories/ingest` accepts:

{
    "url": "https://github.com/owner/repo",
    "source_path": "",
    "assets": [],
    "summary": null,
    "documentation": [],
    "design": null
}

Flow:
1. Repository is fetched from `url` when `source_path` is empty.
2. Supported text/code files are split into line-driven chunks.
3. Embeddings are generated for each chunk and stored in `chunks`.
4. Summary/setup/architecture/design text artifacts are generated and stored in `repositories`.
5. Images and documents discovered in the repo are uploaded to Cloudinary and saved as URLs in `assets`/`documentation`.

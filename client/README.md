# Codesense Client

The client is a React + Vite application that connects to the Codesense FastAPI backend.

## Run locally

1. Open a terminal in `client/`
2. Install dependencies:

```powershell
npm install
```

3. Start the development server:

```powershell
npm run dev
```

4. Open the browser at the URL shown by Vite (usually `http://localhost:5173`).

## Features

- Authentication and project dashboard
- Repository ingestion form
- Repository summary and diagram viewer
- Interactive AI chatbot for repository questions

## Notes

- The client expects the API at `http://localhost:8000`
- If you change the backend port, update `client/src/App.jsx` `API_BASE`
- Mermaid diagrams are rendered using the installed `mermaid` package

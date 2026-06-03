# importing all the needed modules
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.documents import Document
from app.core.config import settings


# defining the repo analyzer class
class RepoAnalyzer:

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GEMINI_API_KEY
        )

    # function to analyze the repo
    def analyze(self, chunks: list[Document]) -> dict:
        context = "\n\n".join([c.page_content for c in chunks[:50]])

        prompt = f"""
You are a code analysis expert. Analyze the following codebase and return a JSON object with these exact keys:

- description: one line description of the project
- summary: 3-5 sentence summary of what the project does
- technologies: list of technologies, frameworks and languages used
- setup_guide: step by step instructions to set up and run the project locally
- workflow_diagram: a mermaid flowchart string showing the main workflow
- architecture_diagram: a mermaid flowchart string showing the system architecture
- er_diagram: a mermaid erDiagram string showing data models and their relationships

Codebase:
{context}

Return only valid JSON, no markdown, no explanation.
"""
        response = self.llm.invoke(prompt)
        text = getattr(response, "content", "").strip()

        # Robustly extract JSON block
        start_idx = text.find("{")
        end_idx = text.rfind("}")
        if start_idx != -1 and end_idx != -1:
            json_str = text[start_idx:end_idx + 1]
        else:
            json_str = text

        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return {
                "description": "Unable to generate a structured description.",
                "summary": "The repository analysis could not be parsed cleanly.",
                "technologies": [],
                "setup_guide": "Review the repository files and run the project locally.",
                "workflow_diagram": "flowchart TD\n  A[Start] --> B[Review code]",
                "architecture_diagram": "flowchart TD\n  A[Client] --> B[Server]",
                "er_diagram": "erDiagram\n  USER ||--o{ PROJECT : owns",
            }
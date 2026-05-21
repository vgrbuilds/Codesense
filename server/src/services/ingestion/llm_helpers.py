#importing all the necessary modules
import asyncio
from pathlib import Path
from typing import Optional, List
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from src.core.config import config
from src.services.ingestion.file_helpers import walk_text_files


#method to get chat llm client
def _get_llm() -> ChatGoogleGenerativeAI | None:
    if not config.gemini_key:
        return None
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=config.gemini_key,
        temperature=0.2,
    )


#method to run a langchain prompt safely
async def run_prompt(template: str, variables: dict[str, str]) -> str:
    llm = _get_llm()
    if not llm:
        return ""

    chain = PromptTemplate.from_template(template) | llm | StrOutputParser()
    try:
        return await asyncio.to_thread(chain.invoke, variables)
    except Exception:
        return ""


#method to generate repository summary
async def generate_repository_summary(root: Path, readme_text: Optional[str] = None) -> str:
    # Prefer README content if provided from GitHub API
    if readme_text:
        return await run_prompt(
            "Summarize the following repository README in 3 concise paragraphs:\n\n{content}",
            {"content": readme_text[:15000]},
        )

    readme = root / "README.md"
    if readme.exists():
        try:
            content = readme.read_text(encoding="utf-8", errors="ignore")
            return await run_prompt(
                "Summarize the following repository README in 3 concise paragraphs:\n\n{content}",
                {"content": content[:15000]},
            )
        except Exception:
            pass

    sample_texts = []
    for i, p in enumerate(walk_text_files(root)):
        if i >= 10:
            break
        try:
            sample_texts.append(Path(p).read_text(encoding="utf-8", errors="ignore")[:5000])
        except Exception:
            continue

    if not sample_texts:
        return ""

    return await run_prompt(
        (
            "You are an assistant that writes a concise summary for a code repository. "
            "Based on the following file excerpts, produce a 3-paragraph high-level summary of the project, its purpose, and main components:\n\n{content}"
        ),
        {"content": "\n\n---\n\n".join(sample_texts)},
    )


#method to generate setup guide
async def generate_setup_guide(root: Path, readme_text: Optional[str] = None) -> str:
    # Prefer README content if available
    if readme_text:
        return await run_prompt(
            (
                "Create a concise setup and run guide for this repository. Provide required steps, dependencies, and example commands. "
                "If sections are missing, infer reasonable defaults based on the code.\n\n{content}"
            ),
            {"content": readme_text[:15000]},
        )

    readme = root / "README.md"
    readme_text_local = ""
    if readme.exists():
        try:
            readme_text_local = readme.read_text(encoding="utf-8", errors="ignore")[:15000]
        except Exception:
            readme_text_local = ""

    return await run_prompt(
        (
            "Create a concise setup and run guide for this repository. Provide required steps, dependencies, and example commands. "
            "If sections are missing, infer reasonable defaults based on the code.\n\n{content}"
        ),
        {"content": readme_text_local},
    )


#method to generate architecture overview
async def generate_architecture_diagram(root: Path, file_list: Optional[List[str]] = None) -> str:
    files = file_list or []
    if not files:
        for i, p in enumerate(walk_text_files(root)):
            if i >= 200:
                break
            try:
                files.append(str(Path(p).relative_to(root)).replace("\\", "/"))
            except Exception:
                continue

    sample = "\n".join(files[:200])
    return await run_prompt(
        (
            "Produce an architecture overview and a textual diagram for this repository. "
            "List main components, their responsibilities, and how they interact. Provide a simple ASCII or Mermaid-style diagram when possible.\n\nFiles:\n{content}"
        ),
        {"content": sample},
    )


#method to generate design description text
async def generate_design_document(root: Path, file_list: Optional[List[str]] = None) -> str:
    files = file_list or []
    if not files:
        for i, p in enumerate(walk_text_files(root)):
            if i >= 200:
                break
            try:
                files.append(str(Path(p).relative_to(root)).replace("\\", "/"))
            except Exception:
                continue

    sample = "\n".join(files[:200])
    return await run_prompt(
        (
            "Create a clean textual product design brief for this codebase so a frontend can render it as an image later. "
            "Include sections for title, purpose, key modules, data flow, and visual layout hints. Keep it structured and readable.\n\nFiles:\n{content}"
        ),
        {"content": sample},
    )


#method to generate chunk embedding
async def generate_embedding(text: str) -> list[float]:
    """Generate an embedding vector for a chunk using Gemini."""
    if not config.gemini_key:
        raise RuntimeError("GEMINI_KEY is not configured in the environment")

    if not text:
        return []

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=config.gemini_key,
    )

    return await asyncio.to_thread(embeddings.embed_query, text)

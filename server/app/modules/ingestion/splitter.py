from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
from langchain_core.documents import Document

LANGUAGE_MAP = {
    ".py":   Language.PYTHON,
    ".js":   Language.JS,
    ".ts":   Language.JS,
    ".jsx":  Language.JS,
    ".tsx":  Language.JS,
    ".go":   Language.GO,
    ".java": Language.JAVA,
    ".rs":   Language.RUST,
    ".cpp":  Language.CPP,
    ".c":    Language.C,
    ".md":   Language.MARKDOWN,
}

class RepoSplitter:

    def split(self, docs: list[Document]) -> list[Document]:
        all_chunks = []

        for doc in docs:
            ext = Path(doc.metadata.get("source", "")).suffix
            splitter = self._get_splitter(ext)
            chunks = splitter.split_documents([doc])

            for i, chunk in enumerate(chunks):
                chunk.metadata["chunk_index"] = i
                chunk.metadata["total_chunks"] = len(chunks)
                chunk.metadata["extension"] = ext

            all_chunks.extend(chunks)

        return all_chunks

    def _get_splitter(self, ext: str):
        language = LANGUAGE_MAP.get(ext)

        if language:
            return RecursiveCharacterTextSplitter.from_language(
                language=language,
                chunk_size=1500,
                chunk_overlap=200,
            )
        return RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
        )
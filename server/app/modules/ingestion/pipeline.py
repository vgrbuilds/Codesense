from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_core.documents import Document
from app.core.config import settings
from .loader import RepoLoader
from .splitter import RepoSplitter


class IngestionPipeline:

    def __init__(self):
        self.splitter = RepoSplitter()
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="gemini-embedding-2",
            google_api_key=settings.GEMINI_API_KEY
        )

    def run(self, repo_url: str, collection) -> dict:
        # 1 - load
        print(f"Loading {repo_url}...")
        docs = RepoLoader(repo_url).load()
        print(f"  {len(docs)} files loaded")

        # 2 - chunk
        print("Chunking...")
        chunks = self.splitter.split(docs)
        print(f"  {len(chunks)} chunks created")

        # Tag each chunk with the source repository URL so that later
        # we can associate them with the correct repo record.
        for chunk in chunks:
            chunk.metadata["repo_url"] = repo_url

        # 3 - embed + store
        print("Embedding and storing...")
        MongoDBAtlasVectorSearch.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            collection=collection,
            index_name="vector_index",
        )
        print("  Done")

        return {
            "files_loaded": len(docs),
            "chunks_created": len(chunks),
            "chunks": chunks,
        }
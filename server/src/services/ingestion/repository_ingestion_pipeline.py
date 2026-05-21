#importing all the necessary modules
from pathlib import Path
import shutil
from typing import Any
from src.db.mongo import MongoDB
from src.models.repository import RepositoryModel
from src.schemas.repository import RepositoryCreateSchema
from src.services.github_service import GitHubService
from src.services.ingestion.asset_uploads import upload_repository_assets
from src.services.ingestion.chunk_persistence import build_chunks, insert_chunks_in_batches
from src.services.ingestion.ingestion_context import IngestionContext
from src.services.ingestion.llm_helpers import (
    generate_architecture_diagram,
    generate_design_document,
    generate_repository_summary,
    generate_setup_guide,
)
from src.services.policies import normalize_repository_url


#method to fetch repository locally and enrich metadata context
async def prepare_source_context(source_path: str, repository_data: RepositoryCreateSchema, context: IngestionContext) -> dict[str, Any] | None:
    if repository_data.url and (not source_path or source_path.strip() == ""):
        # Prefer downloading the archive (no git required); fall back to clone
        try:
            context.repo_local_path = await GitHubService.download_archive_to_temp(repository_data.url)
        except Exception:
            try:
                context.repo_local_path = await GitHubService.clone_repository_to_temp(repository_data.url)
            except Exception as e:
                return {"success": False, "message": f"Failed to fetch repository: {e}"}

        # Enrich LLM inputs via GitHub API
        try:
            context.readme_text = await GitHubService.get_readme_text(repository_data.url)
        except Exception:
            context.readme_text = ""
        try:
            context.file_list = await GitHubService.list_files(repository_data.url)
        except Exception:
            context.file_list = []

    root_path = context.repo_local_path or source_path
    context.root = Path(root_path)
    if not context.root.exists() or not context.root.is_dir():
        return {"success": False, "message": f"Repository path not found: {root_path}"}
    return None


#method to create repository record before chunk persistence
async def create_repository_record(repository_data: RepositoryCreateSchema, context: IngestionContext) -> None:
    context.repository_doc = RepositoryModel(
        url=repository_data.url,
        assets=repository_data.assets,
        summary=repository_data.summary,
        documentation=repository_data.documentation,
        design=repository_data.design,
    )
    repository_result = await MongoDB.database["repositories"].insert_one(context.repository_doc.model_dump())
    context.repository_inserted_id = repository_result.inserted_id
    context.repository_id = str(repository_result.inserted_id)


#method to create and persist all repository chunks
async def create_and_persist_chunks(context: IngestionContext) -> dict[str, Any] | None:
    context.chunks, context.files_scanned = await build_chunks(
        root=context.root,
        repository_id=context.repository_id,
    )
    if not context.chunks:
        await MongoDB.database["repositories"].delete_one({"_id": context.repository_inserted_id})
        return {
            "success": False,
            "message": "No supported text files were found in the repository path.",
            "files_scanned": context.files_scanned,
        }
    await insert_chunks_in_batches(context.chunks)
    return None


#method to generate and store repository artifacts
async def generate_and_store_artifacts(context: IngestionContext) -> None:
    summary = await generate_repository_summary(context.root, readme_text=context.readme_text)
    setup_guide = await generate_setup_guide(context.root, readme_text=context.readme_text)
    architecture = await generate_architecture_diagram(context.root, file_list=context.file_list)
    design = await generate_design_document(context.root, file_list=context.file_list)
    context.uploaded_assets, context.uploaded_documents = await upload_repository_assets(
        root=context.root,
        repository_id=context.repository_id,
    )

    # store generated artifacts
    update_fields: dict[str, Any] = {}
    if summary:
        update_fields["summary"] = summary
    if design:
        update_fields["design"] = design
    elif architecture:
        # fallback to architecture text when design generation is unavailable
        update_fields["design"] = architecture
    docs: list[dict[str, Any]] = context.repository_doc.documentation or []
    if setup_guide:
        docs.append({"type": "setup_guide", "content": setup_guide})
    if architecture:
        docs.append({"type": "architecture", "content": architecture})
    docs.extend(context.uploaded_documents)
    if context.uploaded_assets:
        update_fields["assets"] = (context.repository_doc.assets or []) + context.uploaded_assets
    if docs:
        update_fields["documentation"] = docs

    if update_fields:
        await MongoDB.database["repositories"].update_one({"_id": context.repository_inserted_id}, {"$set": update_fields})


#method to cleanup temporary repository directory
def cleanup_temp_repository(context: IngestionContext) -> None:
    if context.repo_local_path:
        try:
            shutil.rmtree(context.repo_local_path)
        except Exception:
            pass


#method to execute full ingestion pipeline
async def ingest_repository_pipeline(source_path: str, repository_data: RepositoryCreateSchema) -> dict[str, Any]:
    repository_data.url = normalize_repository_url(repository_data.url)
    if repository_data.url:
        existing_repository = await MongoDB.database["repositories"].find_one({"url": repository_data.url})
        if existing_repository:
            return {
                "success": True,
                "repository_id": str(existing_repository["_id"]),
                "files_scanned": 0,
                "chunks_created": 0,
                "assets_uploaded": 0,
                "documents_uploaded": 0,
                "reused": True,
            }

    context = IngestionContext()
    prepare_result = await prepare_source_context(source_path, repository_data, context)
    if prepare_result:
        return prepare_result

    await create_repository_record(repository_data, context)

    chunk_result = await create_and_persist_chunks(context)
    if chunk_result:
        cleanup_temp_repository(context)
        return chunk_result

    try:
        await generate_and_store_artifacts(context)
    finally:
        cleanup_temp_repository(context)

    return {
        "success": True,
        "repository_id": context.repository_id,
        "files_scanned": context.files_scanned,
        "chunks_created": len(context.chunks),
        "assets_uploaded": len(context.uploaded_assets),
        "documents_uploaded": len(context.uploaded_documents),
    }

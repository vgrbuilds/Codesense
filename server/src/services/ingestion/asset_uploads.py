#importing all the necessary modules
from pathlib import Path
from typing import Any
from src.services.cloudinary_service import CloudinaryService
from src.services.ingestion.file_helpers import is_document_file, is_image_file


#method to upload image and document assets to cloudinary
async def upload_repository_assets(root: Path, repository_id: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    assets: list[dict[str, Any]] = []
    documents: list[dict[str, Any]] = []

    for file_path in root.rglob("*"):
        if not file_path.is_file():
            continue

        try:
            relative_path = str(file_path.relative_to(root)).replace("\\", "/")
        except Exception:
            relative_path = file_path.name

        try:
            if is_image_file(file_path):
                uploaded = await CloudinaryService.upload_local_file(
                    file_path=file_path,
                    folder=f"codesense/repositories/{repository_id}/images",
                    resource_type="image",
                )
                assets.append(
                    {
                        "type": "image",
                        "file_path": relative_path,
                        "url": uploaded.get("secure_url"),
                        "public_id": uploaded.get("public_id"),
                    }
                )
            elif is_document_file(file_path):
                uploaded = await CloudinaryService.upload_local_file(
                    file_path=file_path,
                    folder=f"codesense/repositories/{repository_id}/documents",
                    resource_type="raw",
                )
                documents.append(
                    {
                        "type": "document",
                        "file_path": relative_path,
                        "url": uploaded.get("secure_url"),
                        "public_id": uploaded.get("public_id"),
                    }
                )
        except Exception:
            # keep ingestion resilient even if some asset uploads fail
            continue

    return assets, documents

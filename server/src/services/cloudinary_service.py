#importing all the necessary modules
import asyncio
from pathlib import Path
from typing import Any
import cloudinary
import cloudinary.uploader
from src.core.config import config


# defining cloudinary service class
class CloudinaryService:
    #method to configure cloudinary client
    @staticmethod
    def _configure() -> None:
        cloud_name = getattr(config, "cloudinary_cloud_name", None)
        api_key = getattr(config, "cloudinary_api_key", None)
        api_secret = getattr(config, "cloudinary_api_secret", None)

        if not cloud_name or not api_key or not api_secret:
            raise RuntimeError("Cloudinary credentials are not configured in the environment")

        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True,
        )

    #method to upload a local file to cloudinary
    @staticmethod
    async def upload_local_file(file_path: Path, folder: str, resource_type: str = "auto") -> dict[str, Any]:
        CloudinaryService._configure()

        def upload() -> dict[str, Any]:
            result = cloudinary.uploader.upload(
                str(file_path),
                folder=folder,
                resource_type=resource_type,
                use_filename=True,
                unique_filename=True,
                overwrite=False,
            )
            return result

        return await asyncio.to_thread(upload)

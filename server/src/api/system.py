# import all the necessary modules
from fastapi import APIRouter
from src.db.mongo import MongoDB

# defining the router
router = APIRouter(tags=["system"])


# endpoint for health check
@router.get("/health")
async def health():
    return {"success": True, "status": "ok"}


# endpoint for readiness check
@router.get("/ready")
async def ready():
    try:
        await MongoDB.database.command("ping")
        return {"success": True, "status": "ready"}
    except Exception:
        return {"success": False, "status": "not_ready"}

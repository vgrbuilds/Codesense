# importing all the necessary modules
from datetime import datetime, timedelta


# defining all business policy constants
DEFAULT_CREDITS = 10
CREDIT_COST_PER_PROJECT = 2
CREDITS_RESET_DAYS = 30


#method to normalize a repository url for dedup checks
def normalize_repository_url(url: str) -> str:
    normalized = (url or "").strip()
    if normalized.endswith("/"):
        normalized = normalized[:-1]
    if normalized.endswith(".git"):
        normalized = normalized[:-4]
    return normalized


#method to determine whether credits should reset for this user
def should_reset_credits(last_reset_at: datetime | None, now: datetime) -> bool:
    if not last_reset_at:
        return True
    return (now - last_reset_at) >= timedelta(days=CREDITS_RESET_DAYS)

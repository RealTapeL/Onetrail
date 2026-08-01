from fastapi import APIRouter

router = APIRouter(tags=["基础能力"])


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


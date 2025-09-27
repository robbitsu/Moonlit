import time

from fastapi import APIRouter


router = APIRouter(tags=["core"])


@router.get("/")
async def root():
    return {"message": "Hello World"}


@router.get("/health")
async def health_check():
    return {"status": "healthy", "time": time.time()}



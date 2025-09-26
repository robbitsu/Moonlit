import asyncio
import time
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from fastapi import FastAPI

from database import SessionLocal, engine, Base, DATABASE_URL


def _build_alembic_config() -> AlembicConfig:
    cfg = AlembicConfig()
    api_dir = Path(__file__).resolve().parents[1]

    cfg.set_main_option("script_location", str(api_dir / "alembic"))
    cfg.set_main_option("sqlalchemy.url", DATABASE_URL)

    return cfg


async def _apply_db_migrations():
    cfg = _build_alembic_config()
    try:
        await asyncio.to_thread(alembic_command.upgrade, cfg, "head")
    except Exception as exc:
        # Proceed with startup even if migrations fail; log for visibility
        print(f"Alembic migration failed: {exc}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await _apply_db_migrations()
    yield


app = FastAPI(title="Moonlit API", version="1.0.0", lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "time": time.time()}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8123)
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
import logging

import uvicorn
from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from fastapi import FastAPI

from database import DATABASE_URL

from routers.core import router as core_router
from routers.players import router as players_router
from routers.covens import router as covens_router


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
        logging.getLogger("moonlit.api").exception("Alembic migration failed")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await _apply_db_migrations()
    yield


app = FastAPI(title="Moonlit API", version="1.0.0", lifespan=lifespan)

app.include_router(core_router)
app.include_router(players_router)
app.include_router(covens_router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8123)
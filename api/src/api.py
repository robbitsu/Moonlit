import asyncio
import time
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from fastapi import FastAPI, HTTPException

from database import SessionLocal, DATABASE_URL, Player
from schemas import PlayerCreate, PlayerUpdate, PlayerRead


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


@app.post("/players")
async def create_player(new_player: PlayerCreate) -> PlayerRead:
    db_player = Player(**new_player.model_dump())
    with SessionLocal() as session:
        session.add(db_player)
        session.commit()
        session.refresh(db_player)
        return PlayerRead.model_validate(db_player)

@app.get("/players/{player_id}")
async def get_player(player_id: int) -> PlayerRead:
    with SessionLocal() as session:
        player = session.get(Player, player_id)
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        # Validate the player using the Pydantic model
        return PlayerRead.model_validate(player)

@app.put("/players/{player_id}")
async def update_player(player_id: int, player: PlayerUpdate) -> PlayerRead:
    # Get the player from the database
    with SessionLocal() as session:
        db_player = session.get(Player, player_id)
        if not db_player:
            raise HTTPException(status_code=404, detail="Player not found")
        db_player.name = player.name
        db_player.coven_id = player.coven_id
        session.commit()
        session.refresh(db_player)
        return PlayerRead.model_validate(db_player)

@app.delete("/players/{player_id}")
async def delete_player(player_id: int):
    with SessionLocal() as session:
        player = session.get(Player, player_id)
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        session.delete(player)
        session.commit()
        return {"message": "Player deleted"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8123)
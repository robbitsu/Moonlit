import asyncio
import time
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from fastapi import FastAPI, HTTPException

from database import SessionLocal, DATABASE_URL, Player, Coven
from schemas import PlayerCreate, PlayerUpdate, PlayerRead, CovenCreate, CovenRead, CovenUpdate


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


# Player API
@app.post("/players")
async def create_player(new_player: PlayerCreate) -> PlayerRead:
    # Check if the player already exists
    with SessionLocal() as session:
        player = session.get(Player, new_player.id)
        if player:
            raise HTTPException(status_code=400, detail="Player already exists")

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
        # Covens are handled by the player-coven API
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

# Coven API
@app.post("/covens")
async def create_coven(new_coven: CovenCreate) -> CovenRead:
    db_coven = Coven(**new_coven.model_dump())
    with SessionLocal() as session:
        session.add(db_coven)
        session.commit()
        session.refresh(db_coven)
        return CovenRead.model_validate(db_coven)

@app.put("/covens/{coven_id}")
async def update_coven(coven_id: int, coven: CovenUpdate) -> CovenRead:
    with SessionLocal() as session:
        db_coven = session.get(Coven, coven_id)
        if not db_coven:
            raise HTTPException(status_code=404, detail="Coven not found")
        db_coven.name = coven.name
        db_coven.description = coven.description
        session.commit()
        session.refresh(db_coven)
        return CovenRead.model_validate(db_coven)

@app.delete("/covens/{coven_id}")
async def delete_coven(coven_id: int):
    with SessionLocal() as session:
        coven = session.get(Coven, coven_id)
        if not coven:
            raise HTTPException(status_code=404, detail="Coven not found")
        session.delete(coven)
        session.commit()
        return {"message": "Coven deleted"}

@app.get("/covens/{coven_id}/players")
async def get_players_in_coven(coven_id: int) -> list[PlayerRead]:
    with SessionLocal() as session:
        players = session.query(Player).filter(Player.coven_id == coven_id).all()
        return [PlayerRead.model_validate(player) for player in players]

#Player-Coven API
@app.post("/players/{player_id}/covens/{coven_id}")
async def add_player_to_coven(player_id: int, coven_id: int) -> PlayerRead:
    with SessionLocal() as session:
        player = session.get(Player, player_id)
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        coven = session.get(Coven, coven_id)
        if not coven:
            raise HTTPException(status_code=404, detail="Coven not found")
        player.coven_id = coven_id
        session.commit()
        session.refresh(player)
        return PlayerRead.model_validate(player)

@app.delete("/players/{player_id}/covens/{coven_id}")
async def remove_player_from_coven(player_id: int, coven_id: int):
    with SessionLocal() as session:
        player = session.get(Player, player_id)
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        player.coven_id = None
        session.commit()
        session.refresh(player)
        return PlayerRead.model_validate(player)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8123)
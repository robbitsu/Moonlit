import asyncio
import time
from contextlib import asynccontextmanager
from pathlib import Path
import logging

import uvicorn
from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from fastapi import FastAPI, HTTPException, Depends, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import select

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
        logging.getLogger("moonlit.api").exception("Alembic migration failed")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await _apply_db_migrations()
    yield


app = FastAPI(title="Moonlit API", version="1.0.0", lifespan=lifespan)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "time": time.time()}


# Player API
@app.post("/players", response_model=PlayerRead, status_code=201)
async def create_player(new_player: PlayerCreate, db: Session = Depends(get_db)) -> PlayerRead:
    db_player = Player(**new_player.model_dump())
    try:
        db.add(db_player)
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Player already exists")
    db.refresh(db_player)
    return PlayerRead.model_validate(db_player)

@app.get("/players/{player_id}", response_model=PlayerRead)
async def get_player(player_id: int, db: Session = Depends(get_db)) -> PlayerRead:
    player = db.get(Player, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return PlayerRead.model_validate(player)

@app.put("/players/{player_id}", response_model=PlayerRead)
async def update_player(player_id: int, player: PlayerUpdate, db: Session = Depends(get_db)) -> PlayerRead:
    db_player = db.get(Player, player_id)
    if not db_player:
        raise HTTPException(status_code=404, detail="Player not found")
    if player.name is not None:
        db_player.name = player.name
    db.flush()
    db.refresh(db_player)
    return PlayerRead.model_validate(db_player)

@app.delete("/players/{player_id}", status_code=204)
async def delete_player(player_id: int, db: Session = Depends(get_db)):
    player = db.get(Player, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    db.delete(player)
    return Response(status_code=204)

# Coven API
@app.post("/covens", response_model=CovenRead, status_code=201)
async def create_coven(new_coven: CovenCreate, db: Session = Depends(get_db)) -> CovenRead:
    db_coven = Coven(**new_coven.model_dump())
    try:
        db.add(db_coven)
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Coven name already exists")
    db.refresh(db_coven)
    return CovenRead.model_validate(db_coven)

@app.get("/covens/{coven_id}", response_model=CovenRead)
async def get_coven(coven_id: int, db: Session = Depends(get_db)) -> CovenRead:
    coven = db.get(Coven, coven_id)
    if not coven:
        raise HTTPException(status_code=404, detail="Coven not found")
    return CovenRead.model_validate(coven)

@app.put("/covens/{coven_id}", response_model=CovenRead)
async def update_coven(coven_id: int, coven: CovenUpdate, db: Session = Depends(get_db)) -> CovenRead:
    db_coven = db.get(Coven, coven_id)
    if not db_coven:
        raise HTTPException(status_code=404, detail="Coven not found")
    if coven.name is not None:
        db_coven.name = coven.name
    if coven.description is not None:
        db_coven.description = coven.description
    db.flush()
    db.refresh(db_coven)
    return CovenRead.model_validate(db_coven)

@app.delete("/covens/{coven_id}", status_code=204)
async def delete_coven(coven_id: int, db: Session = Depends(get_db)):
    coven = db.get(Coven, coven_id)
    if not coven:
        raise HTTPException(status_code=404, detail="Coven not found")
    has_players = db.scalar(select(Player.id).where(Player.coven_id == coven_id).limit(1)) is not None
    if has_players:
        raise HTTPException(status_code=409, detail="Coven has players; remove players first")
    db.delete(coven)
    return Response(status_code=204)

@app.get("/covens/{coven_id}/players", response_model=list[PlayerRead])
async def get_players_in_coven(coven_id: int, db: Session = Depends(get_db)) -> list[PlayerRead]:
    if not db.get(Coven, coven_id):
        raise HTTPException(status_code=404, detail="Coven not found")
    players = db.scalars(select(Player).where(Player.coven_id == coven_id)).all()
    return [PlayerRead.model_validate(player) for player in players]

#Player-Coven API
@app.post("/players/{player_id}/covens/{coven_id}", response_model=PlayerRead)
async def add_player_to_coven(player_id: int, coven_id: int, db: Session = Depends(get_db)) -> PlayerRead:
    player = db.get(Player, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    coven = db.get(Coven, coven_id)
    if not coven:
        raise HTTPException(status_code=404, detail="Coven not found")
    player.coven_id = coven_id
    db.flush()
    db.refresh(player)
    return PlayerRead.model_validate(player)

@app.delete("/players/{player_id}/covens/{coven_id}", response_model=PlayerRead)
async def remove_player_from_coven(player_id: int, coven_id: int, db: Session = Depends(get_db)) -> PlayerRead:
    player = db.get(Player, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    if player.coven_id != coven_id:
        raise HTTPException(status_code=400, detail="Player not in specified coven")
    player.coven_id = None
    db.flush()
    db.refresh(player)
    return PlayerRead.model_validate(player)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8123)
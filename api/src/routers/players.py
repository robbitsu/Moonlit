from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import Player, Coven
from dependencies import get_db
from schemas import PlayerCreate, PlayerUpdate, PlayerRead


router = APIRouter(prefix="/players", tags=["players"])


@router.post("", response_model=PlayerRead, status_code=201)
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


@router.get("/{player_id}", response_model=PlayerRead)
async def get_player(player_id: int, db: Session = Depends(get_db)) -> PlayerRead:
    player = db.get(Player, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return PlayerRead.model_validate(player)


@router.put("/{player_id}", response_model=PlayerRead)
async def update_player(player_id: int, player: PlayerUpdate, db: Session = Depends(get_db)) -> PlayerRead:
    db_player = db.get(Player, player_id)
    if not db_player:
        raise HTTPException(status_code=404, detail="Player not found")
    if player.name is not None:
        db_player.name = player.name
    db.flush()
    db.refresh(db_player)
    return PlayerRead.model_validate(db_player)


@router.delete("/{player_id}", status_code=204)
async def delete_player(player_id: int, db: Session = Depends(get_db)):
    player = db.get(Player, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    db.delete(player)
    return Response(status_code=204)


@router.post("/{player_id}/covens/{coven_id}", response_model=PlayerRead)
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


@router.delete("/{player_id}/covens/{coven_id}", response_model=PlayerRead)
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



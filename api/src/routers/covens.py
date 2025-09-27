from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import select

from database import Coven, Player
from dependencies import get_db
from schemas import CovenCreate, CovenRead, CovenUpdate, PlayerRead


router = APIRouter(prefix="/covens", tags=["covens"])


@router.post("", response_model=CovenRead, status_code=201)
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


@router.get("/{coven_id}", response_model=CovenRead)
async def get_coven(coven_id: int, db: Session = Depends(get_db)) -> CovenRead:
    coven = db.get(Coven, coven_id)
    if not coven:
        raise HTTPException(status_code=404, detail="Coven not found")
    return CovenRead.model_validate(coven)


@router.put("/{coven_id}", response_model=CovenRead)
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


@router.delete("/{coven_id}", status_code=204)
async def delete_coven(coven_id: int, db: Session = Depends(get_db)):
    coven = db.get(Coven, coven_id)
    if not coven:
        raise HTTPException(status_code=404, detail="Coven not found")
    has_players = db.scalar(select(Player.id).where(Player.coven_id == coven_id).limit(1)) is not None
    if has_players:
        raise HTTPException(status_code=409, detail="Coven has players; remove players first")
    db.delete(coven)
    return Response(status_code=204)


@router.get("/{coven_id}/players", response_model=list[PlayerRead])
async def get_players_in_coven(coven_id: int, db: Session = Depends(get_db)) -> list[PlayerRead]:
    if not db.get(Coven, coven_id):
        raise HTTPException(status_code=404, detail="Coven not found")
    players = db.scalars(select(Player).where(Player.coven_id == coven_id)).all()
    return [PlayerRead.model_validate(player) for player in players]



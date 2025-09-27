import datetime as dt
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# Coven Schemas

class CovenBase(BaseModel):
    name: str = Field(min_length=1)
    description: Optional[str] = Field(default=None)


class CovenCreate(CovenBase):
    pass


class CovenUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1)
    description: Optional[str] = Field(default=None)


class CovenRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = Field(default=None)

    model_config = ConfigDict(from_attributes=True)


# Player Schemas

class PlayerBase(BaseModel):
    name: Optional[str] = Field(default=None)


class PlayerCreate(PlayerBase):
    # Primary key is the Discord user id
    id: int


class PlayerUpdate(BaseModel):
    name: Optional[str] = Field(default=None)


class PlayerRead(BaseModel):
    id: int
    name: Optional[str] = None
    coven_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


# InventoryItem Schemas

class InventoryItemBase(BaseModel):
    item_name: str = Field(min_length=1)
    


class InventoryItemCreate(InventoryItemBase):
    quantity: int = Field(default=1, ge=1)


class InventoryItemUpdate(BaseModel):
    item_name: Optional[str] = Field(default=None, min_length=1)
    quantity: Optional[int] = Field(default=None, ge=0)


class InventoryItemRead(BaseModel):
    id: int
    player_id: int
    item_name: str
    quantity: int

    model_config = ConfigDict(from_attributes=True)

class InventoryItemDelete(BaseModel):
    item_name: str = Field(min_length=1)


# Familiar Schemas

class FamiliarBase(BaseModel):
    name: str = Field(min_length=1)
    type: Optional[str] = None


class FamiliarCreate(FamiliarBase):
    player_id: int


class FamiliarUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1)
    type: Optional[str] = None


class FamiliarRead(BaseModel):
    id: int
    player_id: int
    name: str
    type: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# BookOfShadowsEntry Schemas

class BookOfShadowsEntryBase(BaseModel):
    knowledge_key: str = Field(min_length=1)
    unlocked_at: Optional[dt.datetime] = None


class BookOfShadowsEntryCreate(BookOfShadowsEntryBase):
    player_id: int


class BookOfShadowsEntryUpdate(BaseModel):
    knowledge_key: Optional[str] = Field(default=None, min_length=1)
    unlocked_at: Optional[dt.datetime] = None


class BookOfShadowsEntryRead(BaseModel):
    id: int
    player_id: int
    knowledge_key: str
    unlocked_at: dt.datetime

    model_config = ConfigDict(from_attributes=True)



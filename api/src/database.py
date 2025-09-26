import os
import datetime
from sqlalchemy import create_engine, String, Integer, DateTime, ForeignKey, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Mapped, mapped_column

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///test.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Discord users have a player record, and the player record is associated with a coven of players.

class Coven(Base):
    __tablename__ = "covens"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    players: Mapped[list["Player"]] = relationship("Player", back_populates="coven")

    def __repr__(self):
        return f"<Coven {self.name}, {self.id}>"

class Player(Base):
    __tablename__ = "players"
    id: Mapped[int] = mapped_column(primary_key=True, index=True, unique=True) # this is the discord user id
    name: Mapped[str | None] = mapped_column(String, nullable=True) # not discord username; actual 'witch' name
    coven_id: Mapped[int | None] = mapped_column(ForeignKey("covens.id"), nullable=True)
    coven: Mapped["Coven"] = relationship("Coven", back_populates="players")
    inventory: Mapped[list["InventoryItem"]] = relationship("InventoryItem", back_populates="player", cascade="all, delete-orphan")
    familiars: Mapped[list["Familiar"]] = relationship("Familiar", back_populates="player", cascade="all, delete-orphan")
    book_of_shadows: Mapped[list["BookOfShadowsEntry"]] = relationship("BookOfShadowsEntry", back_populates="player", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Player {self.name}, {self.id}>"

class InventoryItem(Base):
    __tablename__ = "inventory_items"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False)
    item_name: Mapped[str] = mapped_column(String, nullable=False)
    quantity: Mapped[int] = mapped_column(default=1)
    player: Mapped["Player"] = relationship("Player", back_populates="inventory")

class Familiar(Base):
    __tablename__ = "familiars"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str | None] = mapped_column(String, nullable=True)
    player: Mapped["Player"] = relationship("Player", back_populates="familiars")

    def __repr__(self):
        return f"<Familiar {self.name}, {self.id}>"

class BookOfShadowsEntry(Base):
    __tablename__ = "book_of_shadows_entries"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False)
    knowledge_key: Mapped[str] = mapped_column(String, nullable=False) # Corresponds to a knowledge file in the knowledge directory
    unlocked_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.datetime.now())
    player: Mapped["Player"] = relationship("Player", back_populates="book_of_shadows")

    def __repr__(self):
        return f"<BookOfShadowsEntry {self.knowledge_key}, {self.id}>"
    
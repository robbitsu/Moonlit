import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.src.database import Base, Coven, Player, InventoryItem, Familiar, BookOfShadowsEntry

import datetime

@pytest.fixture(scope="function")
def session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_create_coven(session):
    coven = Coven(name="Nightshade", description="A secretive coven")
    session.add(coven)
    session.commit()
    assert coven.id is not None
    assert coven.name == "Nightshade"

def test_create_player_and_relationship(session):
    coven = Coven(name="Moonlit", description="Test coven")
    player = Player(id=123, name="Selene", coven=coven)
    session.add(player)
    session.commit()
    assert player.id == 123
    assert player.coven.name == "Moonlit"
    assert coven.players[0].name == "Selene"

def test_inventory_item(session):
    player = Player(id=456, name="Luna")
    item = InventoryItem(item_name="Crystal Ball", quantity=2, player=player)
    session.add(item)
    session.commit()
    assert item.id is not None
    assert item.player.name == "Luna"
    assert player.inventory[0].item_name == "Crystal Ball"

def test_familiar(session):
    player = Player(id=789, name="Morgana")
    familiar = Familiar(name="Shadow", type="Cat", player=player)
    session.add(familiar)
    session.commit()
    assert familiar.id is not None
    assert familiar.player.name == "Morgana"
    assert player.familiars[0].name == "Shadow"

def test_book_of_shadows_entry(session):
    player = Player(id=321, name="Nyx")
    entry = BookOfShadowsEntry(knowledge_key="lunar_magic", player=player)
    session.add(entry)
    session.commit()
    assert entry.id is not None
    assert entry.player.name == "Nyx"
    assert player.book_of_shadows[0].knowledge_key == "lunar_magic"
    assert isinstance(entry.unlocked_at, datetime.datetime)

def test_crud_player(session):
    player = Player(id=654, name="Artemis")
    session.add(player)
    session.commit()
    player.name = "Artemis Updated"
    session.commit()
    updated = session.query(Player).filter_by(id=654).first()
    assert updated.name == "Artemis Updated"
    session.delete(updated)
    session.commit()
    assert session.query(Player).filter_by(id=654).first() is None

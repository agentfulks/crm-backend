"""Pytest fixtures for API tests."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.main import create_app
from app.models.contact import Contact
from app.models.fund import Fund
from app.models.interaction import Interaction
from app.models.meeting import Meeting
from app.models.note import Note
from app.models.outreach_attempt import OutreachAttempt
from app.models.packet import Packet


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Fund.__table__.create(bind=engine)
    Contact.__table__.create(bind=engine)
    Packet.__table__.create(bind=engine)
    Interaction.__table__.create(bind=engine)
    OutreachAttempt.__table__.create(bind=engine)
    Meeting.__table__.create(bind=engine)
    Note.__table__.create(bind=engine)
    yield engine
    Note.__table__.drop(bind=engine)
    Meeting.__table__.drop(bind=engine)
    OutreachAttempt.__table__.drop(bind=engine)
    Interaction.__table__.drop(bind=engine)
    Packet.__table__.drop(bind=engine)
    Contact.__table__.drop(bind=engine)
    Fund.__table__.drop(bind=engine)


@pytest.fixture(scope="session")
def session_factory(engine):
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture(autouse=True)
def clean_tables(engine):
    yield
    with engine.begin() as connection:
        connection.execute(text("DELETE FROM notes"))
        connection.execute(text("DELETE FROM meetings"))
        connection.execute(text("DELETE FROM outreach_attempts"))
        connection.execute(text("DELETE FROM interactions"))
        connection.execute(text("DELETE FROM packets"))
        connection.execute(text("DELETE FROM contacts"))
        connection.execute(text("DELETE FROM funds"))


@pytest.fixture()
def client(session_factory):
    app = create_app()

    def override_get_db():
        db = session_factory()
        try:
            yield db
            db.commit()
        except Exception:  # pragma: no cover - safety net
            db.rollback()
            raise
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def session(session_factory):
    """Provide a database session for service-level tests."""
    db = session_factory()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

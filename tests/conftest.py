import os
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from alembic import command
from alembic.config import Config

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

TEST_DATABASE_URL = os.getenv("DATABASE_TEST_URL")
if not TEST_DATABASE_URL:
    raise RuntimeError("DATABASE_TEST_URL must be set for tests.")

os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from app.main import app  # noqa: E402
from app.persistence.session import get_db  # noqa: E402

engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False)


@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", os.path.join(base_dir, "alembic"))
    alembic_cfg.set_main_option("sqlalchemy.url", TEST_DATABASE_URL)
    command.upgrade(alembic_cfg, "head")
    yield


@pytest.fixture()
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    db = TestingSessionLocal(bind=connection)
    try:
        yield db
    finally:
        db.close()
        transaction.rollback()
        connection.close()


@pytest.fixture()
def client(db_session):
    def _get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from aplicacion.base_de_datos import Base, get_db
from aplicacion.principal import app

from httpx import ASGITransport, AsyncClient

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_tareas.db"

engine_test = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine_test
)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture()
def db_session(setup_database):
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def override_get_db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture()
def client():
    from fastapi.testclient import TestClient

    with TestClient(app) as c:
        yield c

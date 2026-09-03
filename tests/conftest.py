import os

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if TEST_DATABASE_URL is None:
    raise ValueError(
        "La variable TEST_DATABASE_URL no está definida."
    )

test_engine = create_engine(TEST_DATABASE_URL)

@pytest.fixture
def test_session():
    connection = test_engine.connect()
    transaction = connection.begin()

    session = Session(
        bind=connection,
        join_transaction_mode="create_savepoint"
    )

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def override_usuario_session(
    test_session,
    monkeypatch
):
    from contextlib import contextmanager
    from services import usuarios_service

    @contextmanager
    def override_get_session():
        yield test_session

    monkeypatch.setattr(
        usuarios_service,
        "get_session",
        override_get_session
    )

    return test_session

@pytest.fixture
def override_marca_session(
    test_session,
    monkeypatch
):
    from contextlib import contextmanager
    from services import marcas_service

    @contextmanager
    def override_get_session():
        yield test_session

    monkeypatch.setattr(
        marcas_service,
        "get_session",
        override_get_session
    )

    return test_session

@pytest.fixture
def override_perfume_session(
    test_session,
    monkeypatch
):
    from contextlib import contextmanager
    from services import perfumes_service

    @contextmanager
    def override_get_session():
        yield test_session

    monkeypatch.setattr(
        perfumes_service,
        "get_session",
        override_get_session
    )

    return test_session

@pytest.fixture
def override_carrito_session(
    test_session,
    monkeypatch
):
    from contextlib import contextmanager
    from services import carritos_service

    @contextmanager
    def override_get_session():
        yield test_session

    monkeypatch.setattr(
        carritos_service,
        "get_session",
        override_get_session
    )

    return test_session

@pytest.fixture
def override_linea_carrito_session(
    test_session,
    monkeypatch
):
    from contextlib import contextmanager
    from services import linea_carrito_service

    @contextmanager
    def override_get_session():
        yield test_session

    monkeypatch.setattr(
        linea_carrito_service,
        "get_session",
        override_get_session
    )

    return test_session
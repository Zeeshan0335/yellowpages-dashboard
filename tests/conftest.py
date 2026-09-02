"""Shared test fixtures. Patches pymongo with mongomock so no real DB is needed."""
import os

import mongomock
import pytest


@pytest.fixture(scope="session", autouse=True)
def _set_env():
    os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017/test")
    os.environ.setdefault("MONGODB_DB", "test_db")
    os.environ.setdefault("MONGODB_COLLECTION", "businesses")


@pytest.fixture()
def client(monkeypatch, _set_env):
    monkeypatch.setattr("pymongo.MongoClient", mongomock.MongoClient)
    import importlib

    import main
    importlib.reload(main)

    from fastapi.testclient import TestClient
    return TestClient(main.app)

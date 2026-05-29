from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from storage.database import connect, initialize
from storage.repositories import Repository
from storage.seed_local_demo import seed_connection


@pytest.fixture()
def temp_db_path() -> Path:
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp) / "test.sqlite3"


@pytest.fixture()
def seeded_repo(temp_db_path):
    conn = connect(temp_db_path)
    initialize(conn)
    repo = Repository(conn)
    seed_connection(repo)
    conn.commit()
    yield repo
    conn.close()

"""Runtime dependencies shared by route handlers."""

from __future__ import annotations

from backend.config import get_settings
from storage.database import connect, initialize
from storage.repositories import Repository
from storage.seed_local_demo import seed_connection


def get_repository() -> Repository:
    settings = get_settings()
    conn = connect(settings.sqlite_path)
    initialize(conn)
    repo = Repository(conn)
    needs_local_seed = not settings.is_public_demo and not repo.has_market_prices()
    if not repo.get_active_disclaimer() or needs_local_seed:
        seed_connection(repo)
        conn.commit()
    return repo


def get_runtime_context() -> str:
    return get_settings().runtime_context

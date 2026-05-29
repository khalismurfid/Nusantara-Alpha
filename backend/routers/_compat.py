"""Compatibility helpers for optional FastAPI imports."""

from __future__ import annotations

try:
    from fastapi import APIRouter, HTTPException  # type: ignore
except Exception:
    class HTTPException(Exception):
        def __init__(self, status_code: int, detail: object):
            super().__init__(str(detail))
            self.status_code = status_code
            self.detail = detail

    class APIRouter:  # minimal decorator-compatible fallback
        def __init__(self, *args, **kwargs):
            self.routes = []

        def get(self, path: str, **kwargs):
            return self._decorator("GET", path)

        def post(self, path: str, **kwargs):
            return self._decorator("POST", path)

        def _decorator(self, method: str, path: str):
            def wrap(func):
                self.routes.append((method, path, func))
                return func
            return wrap


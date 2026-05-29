"""Prediction audit logging service."""

from __future__ import annotations

from storage.repositories import Repository


class PredictionLoggingService:
    def __init__(self, repo: Repository):
        self.repo = repo

    def log(self, record: dict) -> str:
        sanitized = dict(record)
        error = sanitized.get("error_message")
        if error:
            sanitized["error_message"] = str(error).replace("/Users/", "[redacted]/")[:500]
        return self.repo.log_prediction(sanitized)


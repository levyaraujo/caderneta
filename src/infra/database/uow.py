from __future__ import annotations
from sqlalchemy.orm import Session
from contextlib import AbstractContextManager
from typing import Callable

from src.infra.database.connection import Session
from src.infra.database.repo import RepoEscrita


class UnitOfWork(AbstractContextManager):
    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory

    def __enter__(self) -> UnitOfWork:
        self.session = self.session_factory()
        self.repo_escrita = RepoEscrita(self.session)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.rollback()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

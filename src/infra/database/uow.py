from __future__ import annotations
from sqlalchemy.orm import Session
from contextlib import AbstractContextManager
from typing import Callable, TypeVar, Type

from src.infra.database.connection import Session
from src.infra.database.repo import RepoEscrita, RepoLeitura, RepoBase

T = TypeVar("T")


class UnitOfWork(AbstractContextManager):
    def __init__(self, session_factory: Callable[[], Session]):
        self._session_factory = session_factory
        self.session: Session | None = None
        self.repo_escrita: RepoEscrita | None = None

    def __enter__(self) -> UnitOfWork:
        self.session = self._session_factory()
        self.repo_escrita = RepoEscrita[T](self.session)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.rollback()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

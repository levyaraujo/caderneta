from abc import ABC
from typing import Iterator, Generic, TypeVar

from sqlalchemy.orm import Session

T = TypeVar("T")


class RepoBase(ABC, Generic[T]):
    def __init__(self, session: Session):
        self.session = session


class RepoEscrita(RepoBase[T]):
    def adicionar(self, entidade: T):
        self.session.add(entidade)

    def remover(self, entidade: T):
        self.session.delete(entidade)


class RepoLeitura(RepoBase[T]):
    def __del__(self):
        self.session.close()

    def buscar_todos(self, entidade: T) -> Iterator:
        yield from self.session.query(entidade).all()

from typing import Iterator

from sqlalchemy.orm import Session


class RepoEscrita:
    def __init__(self, session: Session):
        self.session = session

    def __del__(self):
        self.session.rollback()

    def adicionar(self, entidade):
        self.session.add(entidade)

    def remover(self, entidade):
        self.session.delete(entidade)

    def commit(self):
        self.session.commit()


class RepoLeitura:
    def __init__(self, session: Session):
        self.session = session

    def __del__(self):
        self.session.close()

    def buscar_todos(self, modelo) -> Iterator:
        yield from self.session.query(modelo).all()

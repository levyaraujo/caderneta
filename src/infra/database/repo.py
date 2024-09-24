from collections.abc import Iterator

from sqlalchemy.orm import Session


class RepoEscrita:
    def __init__(self, session: Session):
        self.session = session

    def adicionar(self, entidade):
        self.session.add(entidade)

    def remover(self, entidade):
        self.session.delete(entidade)

    def commit(self):
        self.session.commit()


class RepoLeitura:
    def __init__(self, session: Session):
        self.session = session

    def buscar_por_id(self, modelo, id):
        return self.session.query(modelo).get(id)

    def buscar_todos(self, modelo) -> Iterator:
        yield from self.session.query(modelo).all()

from typing import List

from sqlalchemy.orm import Session

from src.dominio.transacao.entidade import Transacao
from src.infra.database.repo import RepoLeitura, RepoEscrita, RepoBase
from src.libs.tipos import Intervalo


class RepoTransacaoEscrita(RepoEscrita):
    def __init__(self, session: Session):
        super().__init__(session=session)


class RepoTransacaoLeitura(RepoBase[Transacao]):
    def buscar_por_intervalo_e_usuario(
        self, intervalo: Intervalo, usuario_id: int
    ) -> List[Transacao]:
        return (
            self.session.query(Transacao)
            .filter(
                Transacao.usuario_id == usuario_id,
                Transacao.caixa >= intervalo.inicio,
                Transacao.caixa <= intervalo.fim,
            )
            .all()
        )

    def buscar_por_id(self, entidade: Transacao):
        return self.session.query(Transacao).filter(Transacao.id == entidade.id).first()

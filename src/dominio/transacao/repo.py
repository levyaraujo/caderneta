from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.dominio.transacao.entidade import Transacao
from src.infra.database.repo import RepoEscrita, RepoBase
from src.libs.tipos import Intervalo


class RepoTransacaoEscrita(RepoEscrita):
    def __init__(self, session: Session):
        super().__init__(session=session)


class RepoTransacaoLeitura(RepoBase[Transacao]):
    def buscar_por_intervalo_e_usuario(self, intervalo: Intervalo, usuario_id: int) -> List[Transacao]:
        return (
            self.session.query(Transacao)
            .filter(
                Transacao.usuario_id == usuario_id,  # type: ignore
                Transacao.caixa >= intervalo.inicio,
                Transacao.caixa <= intervalo.fim,
            )
            .order_by(Transacao.caixa)
            .all()
        )

    def buscar_por_id(self, entidade: Transacao):
        return self.session.query(Transacao).filter(Transacao.id == entidade.id).first()

    def buscar_por_wamid(self, wamid: str, usuario_id: int):
        return (
            self.session.query(Transacao)
            .filter(func.lower(Transacao.wamid) == func.lower(wamid), Transacao.usuario_id == usuario_id)
            .first()
        )

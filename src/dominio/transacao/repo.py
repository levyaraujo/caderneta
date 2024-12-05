from typing import List, Iterator

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.dominio.transacao.entidade import Transacao
from src.dominio.transacao.tipos import TipoTransacao
from src.infra.database.repo import RepoEscrita, RepoBase
from src.libs.tipos import Intervalo


class RepoTransacaoEscrita(RepoEscrita):
    def __init__(self, session: Session):
        super().__init__(session=session)


class RepoTransacaoLeitura(RepoBase[Transacao]):
    def buscar_por_intervalo_e_usuario(self, intervalo: Intervalo, usuario_id: int) -> List[Transacao]:
        transacoes: List[Transacao] = (
            self.session.query(Transacao)
            .filter(
                Transacao.usuario_id == usuario_id,
                Transacao.caixa >= intervalo.inicio,
                Transacao.caixa <= intervalo.fim,
            )
            .order_by(Transacao.caixa)
            .all()
        )
        return transacoes

    def buscar_por_intervalo_usuario_e_tipo(
        self, intervalo: Intervalo, usuario_id: int, tipo: str | TipoTransacao
    ) -> List[Transacao]:
        transacoes: List[Transacao] = (
            self.session.query(Transacao)
            .filter(
                Transacao.usuario_id == usuario_id,
                Transacao.caixa >= intervalo.inicio,
                Transacao.caixa <= intervalo.fim,
                Transacao.tipo == tipo,
            )
            .order_by(Transacao.caixa)
            .all()
        )
        return transacoes

    def buscar_por_intervalo_e_usuario_ordenando_por_data_e_valor(
        self, intervalo: Intervalo, usuario_id: int
    ) -> List[Transacao]:
        transacoes: List[Transacao] = (
            self.session.query(Transacao)
            .filter(
                Transacao.usuario_id == usuario_id,
                Transacao.caixa >= intervalo.inicio,
                Transacao.caixa <= intervalo.fim,
            )
            .order_by(Transacao.caixa, Transacao.valor)
            .all()
        )
        return transacoes

    def buscar_por_id(self, entidade: Transacao) -> Transacao:
        return self.session.query(Transacao).filter(Transacao.id == entidade.id).first()

    def buscar_por_wamid(self, wamid: str, usuario_id: int) -> Transacao:
        return (
            self.session.query(Transacao)
            .filter(func.lower(Transacao.wamid) == func.lower(wamid), Transacao.usuario_id == usuario_id)
            .first()
        )

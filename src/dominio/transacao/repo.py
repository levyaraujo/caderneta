from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.dominio.transacao.entidade import Transacao
from src.dominio.usuario.entidade import Usuario
from src.infra.database.repo import RepoLeitura
from src.libs.tipos import Intervalo


class RepoTransacaoLeitura(RepoLeitura):
    def __init__(self, session: Session):
        super().__init__(session=session)

    def buscar_por_intervalo_e_usuario(self, intervalo: Intervalo, usuario_id: int):
        return (
            self.session.query(Transacao, Usuario)
            .join(
                Usuario,
                and_(
                    Transacao.usuario_id == usuario_id,
                    Transacao.caixa >= intervalo.inicio,
                    Transacao.caixa <= intervalo.fim,
                ),
            )
            .all()
        )

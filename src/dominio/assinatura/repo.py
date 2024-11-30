from typing import Optional

from src.dominio.assinatura.entidade import Assinatura
from src.infra.database.repo import RepoLeitura


class RepoAssinaturaLeitura(RepoLeitura):
    def buscar_por_stripe_subscription_id(self, subscription_id: str) -> Assinatura:
        return self.session.query(Assinatura).filter(Assinatura.stripe_id == subscription_id).first()

    def buscar_por_id_usuario(self, id_usuario: int) -> Assinatura:
        return self.session.query(Assinatura).filter(Assinatura.usuario_id == id_usuario).first()

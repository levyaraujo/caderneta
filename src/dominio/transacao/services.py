import logging
from typing import List

from src.dominio.transacao.excecoes import ErroAoCriarTransacao
from src.dominio.transacao.repo import RepoTransacaoEscrita
from src.dominio.transacao.tipos import TipoTransacao
from src.infra.database.connection import Session
from src.infra.database.uow import UnitOfWork
from src.libs.tipos import Intervalo
from src.dominio.transacao.entidade import Transacao

logger = logging.getLogger("transacao.servicos")


def _calcular_caixa(transacoes: List[Transacao], intervalo: Intervalo):
    transacoes_no_periodo = [
        transacao for transacao in transacoes if intervalo.contem(transacao.caixa)
    ]

    soma = 0

    for transacao in transacoes_no_periodo:
        soma += (
            transacao.valor
            if transacao.tipo == TipoTransacao.CREDITO
            else -transacao.valor
        )

    return soma


def _calcular_competencia(transacoes: List[Transacao], intervalo: Intervalo):
    transacoes_no_periodo = [
        transacao for transacao in transacoes if intervalo.contem(transacao.caixa)
    ]

    soma = 0

    for transacao in transacoes_no_periodo:
        soma += (
            transacao.valor
            if transacao.tipo == TipoTransacao.CREDITO
            else -transacao.valor
        )

    return soma


def criar_transacao(transacao: Transacao, uow: UnitOfWork):
    try:
        with uow:
            uow.repo_escrita.adicionar(transacao)
            uow.commit()
    except Exception as e:
        logger.error(f"Erro ao criar transacao: {e}")
        raise ErroAoCriarTransacao(
            f"Erro ao criar transação para o usuario {transacao.usuario.id}: {e}"
        )

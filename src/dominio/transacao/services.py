import logging
from typing import List

from src.dominio.processamento.entidade import ConstrutorTransacao
from src.dominio.transacao.exceptions import ErroAoCriarTransacao
from src.dominio.transacao.tipos import TipoTransacao
from src.dominio.usuario.entidade import Usuario
from src.infra.database.uow import UnitOfWork
from src.libs.tipos import Intervalo
from src.dominio.transacao.entidade import Transacao, Real


def _calcular_caixa(transacoes: List[Transacao], intervalo: Intervalo) -> float:
    transacoes_no_periodo = [transacao for transacao in transacoes if intervalo.contem(transacao.caixa)]

    soma = 0.0

    for transacao in transacoes_no_periodo:
        soma += transacao.valor if transacao.tipo == TipoTransacao.CREDITO else -transacao.valor

    return soma


def _calcular_competencia(transacoes: List[Transacao], intervalo: Intervalo) -> float:
    transacoes_no_periodo = [transacao for transacao in transacoes if intervalo.contem(transacao.caixa)]

    soma = 0.0

    for transacao in transacoes_no_periodo:
        soma += transacao.valor if transacao.tipo == TipoTransacao.CREDITO else -transacao.valor

    return soma


def salvar_transacao(transacao: Transacao, uow: UnitOfWork):
    try:
        with uow:
            uow.repo_escrita.adicionar(transacao)
            uow.commit()
    except Exception as e:
        logging.error(f"Erro ao criar transação para o usuario {transacao.usuario.email}: {e}")
        raise ErroAoCriarTransacao(f"Erro ao criar transação. Usuario: {transacao.usuario.email}")


def comando_criar_transacao(usuario: Usuario, tipo: str, mensagem: str, uow: UnitOfWork, telefone: str) -> dict:
    parser = ConstrutorTransacao(acao=TipoTransacao[tipo])
    acao = "pagamento" if tipo == "DEBITO" else "recebimento"
    transacao_comando = parser.parse_message(mensagem)
    transacao = Transacao(
        usuario=usuario,
        valor=transacao_comando.valor,
        tipo=transacao_comando.tipo,
        categoria=transacao_comando.categoria,
        caixa=transacao_comando.data,
    )
    salvar_transacao(transacao=transacao, uow=uow)
    mensagem = (
        f"Entendi! Houve um {acao} de {Real(transacao_comando.valor)} no dia {transacao_comando.data_formatada} "
        f"na categoria *{transacao_comando.categoria}*."
    )

    resposta = resposta_comando_transacao(telefone, mensagem)

    return resposta


def resposta_comando_transacao(telefone: str, mensagem: str):
    return {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": telefone,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": mensagem},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "apagar", "title": "Apagar"}},
                    {"type": "reply", "reply": {"id": "lucro", "title": "Lucro"}},
                ]
            },
        },
    }

from src.dominio.bot.entidade import BotBase
from src.dominio.processamento.entidade import ClassificadorTexto, ConstrutorTransacao
from src.dominio.transacao.entidade import Real, Transacao
from src.dominio.transacao.tipos import TipoTransacao


def responder_usuario(mensagem: str, usuario: str, bot: BotBase):
    classifier = ClassificadorTexto()
    tipo, _ = classifier.classificar_mensagem(mensagem)
    if tipo == "debito" or tipo == "credito":
        resposta = comando_criar_transacao(tipo.upper(), mensagem)
    else:
        resposta = f"Você enviou o comando *{tipo}*"
    return bot.responder(resposta, usuario)


def comando_criar_transacao(tipo: str, mensagem: str) -> str:
    parser = ConstrutorTransacao(acao=TipoTransacao[tipo])
    acao = "pagamento" if tipo == "debito" else "recebimento"
    transacao_comando = parser.parse_message(mensagem)
    resposta = f"Entendi! Houve um {acao} de {Real(transacao_comando.valor)} no dia {transacao_comando.data_formatada} na categoria *{transacao_comando.categoria}*."

    return resposta

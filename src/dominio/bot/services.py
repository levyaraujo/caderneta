from src.dominio.bot.entidade import BotBase
from src.dominio.processamento.entidade import ClassificadorTexto, ConstrutorTransacao
from src.dominio.transacao.entidade import Real
from src.dominio.transacao.tipos import TipoTransacao


def responder_usuario(mensagem: str, usuario: str, bot: BotBase):
    classifier = ClassificadorTexto()
    tipo, prob = classifier.classificar_mensagem(mensagem)
    parser = ConstrutorTransacao(acao=TipoTransacao[tipo])
    acao = "pagamento" if tipo == "DEBITO" else "recebimento"
    transacao = parser.parse_message(mensagem)
    probabilidades = ""
    for t, p in prob.items():
        probabilidades += f"{t}: {p}\n"

    resposta = f"Entendi! Houve um {acao} de {Real(transacao.valor)} no dia {transacao.data_formatada} na categoria *{transacao.categoria}*."
    return bot.responder(resposta, usuario)

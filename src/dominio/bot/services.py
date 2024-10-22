from src.dominio.bot.entidade import TwilioBot, BotBase
from src.dominio.processamento.entidade import TextClassifier, FinancialMessageParser
from src.dominio.transacao.tipos import TipoTransacao


def responder_usuario(mensagem: str, usuario: str, bot: BotBase):
    classifier = TextClassifier()
    tipo, prob = classifier.classify_message(mensagem)
    tipo = str(tipo).upper()
    parser = FinancialMessageParser(acao=TipoTransacao[tipo])
    transacao = parser.parse_message(mensagem)
    print(parser.format_transaction(transacao))
    probabilidades = ""
    for t, p in prob.items():
        probabilidades += f"{t}: {p}\n"

    resposta = f"O tipo da mensagem é: {tipo} com as probabilidades: \n{probabilidades}"
    return bot.responder(resposta, usuario)

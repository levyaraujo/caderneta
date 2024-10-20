from src.dominio.bot.entidade import TwilioBot
from src.dominio.processamento.entidade import TextClassifier
import joblib


def responder_usuario(mensagem: str, usuario: str):
    bot = TwilioBot()
    classifier = TextClassifier()
    tipo, prob = classifier.classify_message(mensagem)
    probabilidades = ""
    for t, p in prob.items():
        probabilidades += f"{t}: {p}\n"

    resposta = f"O tipo da mensagem é: {tipo} com as probabilidades: \n{probabilidades}"
    return bot.responder(resposta, usuario)

from src.dominio.bot.entidade import TwilioBot


def responder_usuario(mensagem: str):
    bot = TwilioBot()
    return bot.responder(mensagem)

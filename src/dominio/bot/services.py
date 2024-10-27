from src.dominio.bot.entidade import BotBase
from src.dominio.bot.exceptions import ComandoDesconhecido
from src.dominio.processamento.entidade import ClassificadorTexto, ConstrutorTransacao
from src.dominio.processamento.exceptions import NaoEhTransacao
from src.dominio.transacao.entidade import Real
from src.dominio.transacao.tipos import TipoTransacao
from src.dominio.bot.comandos import bot


async def responder_usuario(
    mensagem: str, usuario: str, nome_usuario: str, robo: BotBase
):
    try:
        resposta = await bot.processar_mensagem(mensagem, nome_usuario=nome_usuario)
        return robo.responder(resposta, usuario)  # type: ignore[arg-type]

    except ComandoDesconhecido:
        try:
            classifier = ClassificadorTexto()
            tipo, _ = classifier.classificar_mensagem(mensagem)
            if tipo == "debito" or tipo == "credito":
                resposta = comando_criar_transacao(tipo.upper(), mensagem)

                return robo.responder(resposta, usuario)
        except NaoEhTransacao:
            robo.responder("Não entendi sua mensagem 🫤", usuario)
            robo.responder(bot.get_help(), usuario)


def comando_criar_transacao(tipo: str, mensagem: str) -> str:
    parser = ConstrutorTransacao(acao=TipoTransacao[tipo])
    acao = "pagamento" if tipo == "debito" else "recebimento"
    transacao_comando = parser.parse_message(mensagem)
    resposta = f"Entendi! Houve um {acao} de {Real(transacao_comando.valor)} no dia {transacao_comando.data_formatada} na categoria *{transacao_comando.categoria}*."

    return resposta

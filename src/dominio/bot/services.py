from src.dominio.bot.entidade import BotBase
from src.dominio.bot.exceptions import ComandoDesconhecido
from src.dominio.processamento.entidade import ClassificadorTexto, ConstrutorTransacao
from src.dominio.transacao.entidade import Real
from src.dominio.transacao.tipos import TipoTransacao
from src.dominio.bot.comandos import gerenciador_comandos


async def responder_usuario(
    mensagem: str, usuario: str, nome_usuario: str, bot: BotBase
):
    try:
        resposta = await gerenciador_comandos.processar_mensagem(
            mensagem, nome_usuario=nome_usuario
        )
        return bot.responder(resposta, usuario)  # type: ignore[arg-type]

    except ComandoDesconhecido:
        classifier = ClassificadorTexto()
        tipo, _ = classifier.classificar_mensagem(mensagem)
        if tipo == "debito" or tipo == "credito":
            resposta = comando_criar_transacao(tipo.upper(), mensagem)

            return bot.responder(resposta, usuario)  # type: ignore[arg-type]


def comando_criar_transacao(tipo: str, mensagem: str) -> str:
    parser = ConstrutorTransacao(acao=TipoTransacao[tipo])
    acao = "pagamento" if tipo == "debito" else "recebimento"
    transacao_comando = parser.parse_message(mensagem)
    resposta = f"Entendi! Houve um {acao} de {Real(transacao_comando.valor)} no dia {transacao_comando.data_formatada} na categoria *{transacao_comando.categoria}*."

    return resposta

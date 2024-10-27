from src.dominio.bot.entidade import GerenciadorComandos
from src.dominio.graficos.services import criar_grafico_fluxo_de_caixa
from src.dominio.transacao.entidade import Real
from src.dominio.transacao.tipos import TipoTransacao
from src.dominio.usuario.entidade import Usuario

bot = GerenciadorComandos()


@bot.comando("olá", "Mostra ajuda", icon="👋🏼")
def saudacao(*args, **kwargs):
    nome_usuario = kwargs.get("nome_usuario")
    return f"Olá, {nome_usuario}! Como posso ajudar?"


@bot.comando("ajuda", "Mostra comandos disponíveis", icon="❓")
def ajuda(*args, **kwargs):
    return bot.get_help()


@bot.comando("listar fluxo", "Lista fluxo de caixa no mês atual", icon="💸")
def listar_fluxo(*args, **kwargs):
    usuario: Usuario = kwargs.get("usuario")
    intervalo = kwargs.get("intervalo")
    transacoes = bot.repo_transacao_leitura.buscar_por_intervalo_e_usuario(
        usuario_id=usuario.id, intervalo=intervalo
    )

    return "\n".join(
        f"{Real(transacao.valor)} - {transacao.categoria} - {transacao.caixa.strftime('%d/%m/%Y')} {'💸' if transacao.tipo == TipoTransacao.CREDITO else '🔻'}"
        for transacao in transacoes
    )


@bot.comando(
    "grafico fluxo", "Devolve gráfico de fluxo de caixa do mês atual", icon="📉"
)
def grafico_fluxo(*args, **kwargs):
    usuario: Usuario = kwargs.get("usuario")
    intervalo = kwargs.get("intervalo")

    transacoes = bot.repo_transacao_leitura.buscar_por_intervalo_e_usuario(
        usuario_id=usuario.id, intervalo=intervalo
    )

    criar_grafico_fluxo_de_caixa(transacoes=transacoes)

from src.dominio.bot.entidade import GerenciadorComandos

gerenciador_comandos = GerenciadorComandos()


@gerenciador_comandos.comando("ola", "Mostra ajuda", ["oi", "olá", "ajuda"])
def comando_saudacao(*args, **kwargs):
    nome_usuario = kwargs.get("nome_usuario")
    return f"Olá {nome_usuario}! Como posso ajudar?"


@gerenciador_comandos.comando("ajuda", "Mostra comandos disponíveis")
def ajuda(*args, **kwargs):
    return gerenciador_comandos.get_help()

from typing import TypeVar

T = TypeVar("T")

TRANSACAO_DEBITO = [
    "paguei",
    "pagamento",
    "p",
    "pp",
    "gastei",
    "compra",
    "pag",
    "comprei",
    "gasto",
    "gastos",
    "pague",
    "pagou",
    "pago",
    "pguei",
    "mercado",
    "compras",
    "pagar",
    "entrada",
    "pagarei",
    "compre",
    "pagui",
    "perdi",
]

TRANSACAO_CREDITO = [
    "recebi",
    "vendi",
    "v",
    "recebimento",
    "r",
    "venda",
    "vendo",
    "rec",
    "entrada",
    "vendido",
    "ganhei",
    "vendeu",
    "recebido",
    "c",
    "recebe",
    "vende",
    "vendas",
    "entrou",
    "reci",
]

REGEX_WAMID = r"^wamid\.[A-Za-z0-9+/]+=$"

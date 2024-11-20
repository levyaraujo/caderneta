import pytest

from src.utils.whatsapp_api import parse_whatsapp_payload
from tests.whatsapp.dados_teste import dados_teste


@pytest.mark.parametrize("payload, mensagem, wamid", dados_teste)
def test_whatsapp_payload_parser(payload, mensagem, wamid):
    dados = parse_whatsapp_payload(payload=payload)
    assert dados.mensagem == mensagem
    assert dados.wamid == wamid

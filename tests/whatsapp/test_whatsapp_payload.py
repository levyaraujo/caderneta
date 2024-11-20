import pytest

from src.utils.whatsapp_api import parse_whatsapp_payload
from tests.whatsapp.dados_teste import dados_teste


@pytest.mark.parametrize("payload, mensagem", dados_teste)
def test_whatsapp_payload_parser(payload, mensagem):
    dados = parse_whatsapp_payload(payload=payload)
    assert dados.mensagem == mensagem

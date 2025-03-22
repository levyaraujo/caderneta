from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import datetime

from src.utils.formatos import formatar_telefone
from src.utils.validadores import limpar_texto


@dataclass
class Contato:
    wa_id: str
    profile: Optional[Dict[str, str]] = None


@dataclass
class Mensagem:
    from_: str
    id: str
    timestamp: datetime
    type: str
    text: Optional[Dict[str, str]] = None
    image: Optional[Dict[str, str]] = None
    video: Optional[Dict[str, str]] = None
    audio: Optional[Dict[str, str]] = None
    document: Optional[Dict[str, str]] = None
    location: Optional[Dict[str, Dict[str, float]]] = None
    interactive: Optional[Dict] = None
    context: Optional[Dict] = None


@dataclass
class Status:
    id: str
    recipient_id: str
    status: str
    timestamp: datetime
    conversation: Optional[Dict] = None
    pricing: Optional[Dict] = None


@dataclass
class WhatsAppPayload:
    nome: str
    mensagem: str
    telefone: str
    object: str
    wamid: str
    audio: Optional[str] = None
    imagem: Optional[str] = None
    contacts: Optional[List[Contato]] = None
    messages: Optional[List[Mensagem]] = None
    statuses: Optional[List[Status]] = None

    def __post_init__(self):
        if self.messages:
            for msg in self.messages:
                if isinstance(msg.timestamp, str):
                    msg.timestamp = datetime.fromtimestamp(int(msg.timestamp))

        if self.statuses:
            for status in self.statuses:
                if isinstance(status.timestamp, str):
                    status.timestamp = datetime.fromtimestamp(int(status.timestamp))


def parse_whatsapp_payload(payload: Dict) -> WhatsAppPayload:
    """
    Formata payload do WhatsApp Business API e transforma em um dataclass estruturado.
    Lida tanto com mensagens de texto, como respostas de botões interativos.

    Args:
        payload (Dict): Payload cru do webhook vindo do WhatsApp Business API

    Returns:
        WhatsAppPayload: Representação estruturada como classe do payload.
    """
    try:
        contacts = [Contato(**contact) for contact in payload.get("contacts", [])]
        messages = [Mensagem(**message) for message in payload.get("messages", [])]
        statuses = [Status(**status) for status in payload.get("statuses", [])]
        base = payload["entry"][0]["changes"][0]["value"]
        nome_usuario = base["contacts"][0]["profile"]["name"]
        telefone = base["contacts"][0]["wa_id"]
        telefone = formatar_telefone(telefone)
        mensagem = ""
        audio = None
        imagem = None

        message_data = base["messages"][0]
        message_type = str(message_data["type"]).lower()

        if message_type == "text":
            mensagem = str(message_data["text"]["body"]).lower()
        if message_type == "audio":
            audio = str(message_data["audio"]["id"])
        elif message_type == "interactive":
            if message_data["interactive"]["type"] == "button_reply":
                mensagem = message_data["interactive"]["button_reply"]["id"]

        elif message_type == "image":
            imagem = message_data["image"]["id"]

        wamid = message_data["id"]

        return WhatsAppPayload(
            object=payload["object"],
            nome=nome_usuario,
            mensagem=limpar_texto(mensagem),
            telefone=telefone,
            wamid=wamid,
            audio=audio,
            imagem=imagem,
        )
    except KeyError:
        pass

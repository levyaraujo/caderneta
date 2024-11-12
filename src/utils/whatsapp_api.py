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
    entry: List[Dict]
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


# Example usage
def parse_whatsapp_payload(payload: Dict) -> WhatsAppPayload:
    """
    Parse a WhatsApp Business API webhook payload into structured dataclasses.

    Args:
        payload (Dict): The raw webhook payload from WhatsApp Business API

    Returns:
        WhatsAppPayload: Structured representation of the webhook data
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
        if str(base["messages"][0]["type"]).lower() == "text":
            mensagem = str(base["messages"][0]["text"]["body"]).lower()

        return WhatsAppPayload(
            object=payload["object"],
            entry=payload["entry"],
            contacts=contacts,
            messages=messages,
            statuses=statuses,
            nome=nome_usuario,
            mensagem=limpar_texto(mensagem),
            telefone=telefone,
        )
    except KeyError:
        pass

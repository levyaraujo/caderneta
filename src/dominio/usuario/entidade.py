from dataclasses import dataclass, field

from src.validadores import validar_email, validar_telefone


@dataclass
class Usuario:
    nome: str
    sobrenome: str
    telefone: str
    email: str
    senha: str
    id: int | None = field(default=None)

    def __post_init__(self):
        validar_email(self.email)
        validar_telefone(self.telefone)

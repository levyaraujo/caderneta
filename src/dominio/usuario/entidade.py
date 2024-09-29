from dataclasses import dataclass

from src.validadores import validar_email, validar_telefone


@dataclass
class Usuario:
    id: int
    nome: str
    sobrenome: str
    telefone: str
    email: str
    senha: str

    def __post_init__(self):
        validar_email(self.email)
        validar_telefone(self.telefone)

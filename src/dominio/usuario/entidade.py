from dataclasses import dataclass, field

from pydantic import BaseModel, EmailStr

from src.utils.validadores import validar_email, validar_telefone


@dataclass
class Usuario:
    nome: str
    sobrenome: str
    telefone: str
    email: str
    senha: str | None = field(default=None)
    id: int | None = field(default=None)

    def __post_init__(self):
        validar_email(self.email)
        validar_telefone(self.telefone)


class UsuarioModel(BaseModel):
    nome: str
    sobrenome: str = ""
    telefone: str
    email: EmailStr
    senha: str | None = None


class UsuarioResposta(BaseModel):
    nome: str
    sobrenome: str
    telefone: str

from enum import Enum

from sqlalchemy.types import TypeDecorator, String


class TipoTransacaoORM(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        if isinstance(value, TipoTransacao):
            return value.value
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return TipoTransacao(value)
        return value


class TipoTransacao(Enum):
    DEBITO = "debito"
    CREDITO = "credito"

from enum import unique

from sqlalchemy import (
    Table,
    Column,
    Integer,
    Float,
    String,
    DateTime,
    ForeignKey,
    Boolean,
    Enum,
    Date,
)
from sqlalchemy.orm import registry, relationship

from src.dominio.assinatura.entidade import StatusAssinatura, Assinatura
from src.dominio.transacao.entidade import Transacao
from src.dominio.transacao.tipos import TipoTransacaoORM
from src.dominio.usuario.entidade import Usuario
from src.infra.database.connection import metadata

mapper = registry(metadata=metadata)

usuarios = Table(
    "usuarios",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("nome", String),
    Column("sobrenome", String),
    Column("telefone", String),
    Column("email", String),
    Column("senha", String, default=None),
)

transacoes = Table(
    "transacoes",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("usuario_id", Integer, ForeignKey("usuarios.id")),
    Column("valor", Float),
    Column("categoria", String),
    Column("tipo", TipoTransacaoORM),
    Column("descricao", String),
    Column("caixa", DateTime),
    Column("competencia", DateTime),
    Column("wamid", String, nullable=False),
)

assinaturas = Table(
    "assinaturas",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("stripe_id", String, unique=True, nullable=False),
    Column("usuario_id", Integer, ForeignKey("usuarios.id"), unique=True),
    Column("plano", String),
    Column("valor_mensal", Float),
    Column("data_inicio", DateTime),
    Column("data_termino", DateTime, nullable=True),
    Column("status", Enum(StatusAssinatura)),
    Column("data_proximo_pagamento", DateTime, nullable=True),
    Column("data_ultimo_pagamento", DateTime, nullable=True),
    Column("renovacao_automatica", Boolean, default=True),
)


def iniciar_mapeamento_orm() -> None:
    if not mapper.mappers:
        mapper.map_imperatively(
            Usuario,
            usuarios,
            properties={
                "assinatura": relationship(
                    Assinatura,
                    uselist=False,
                )
            },
        )
        mapper.map_imperatively(
            Transacao,
            transacoes,
            properties={
                "usuario": relationship(Usuario),
                "usuario_id": transacoes.c.usuario_id,
            },
        )
        mapper.map_imperatively(Assinatura, assinaturas)

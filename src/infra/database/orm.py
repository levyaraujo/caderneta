from sqlalchemy import MetaData, Table, Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import registry, relationship
from src.dominio.transacao.entidade import Transacao
from src.dominio.usuario.entidade import Usuario

metadata = MetaData()
mapper = registry()

usuarios = Table(
    'usuarios',
    metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('nome', String),
    Column('sobrenome', String),
    Column('telefone', String),
    Column('email', String),
    Column('senha', String)
)

transacoes = Table(
    'transacoes',
    metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('usuario_id', Integer, ForeignKey('usuarios.id')),
    Column('valor', Float),
    Column('destino', String),
    Column('tipo', String),
    Column('descricao', String),
    Column('caixa', DateTime)
)

def iniciar_mapeamento_orm():
    mapper.map_imperatively(Usuario, usuarios)
    mapper.map_imperatively(Transacao, transacoes, properties={
        "usuario": relationship(Usuario, back_populates="transacoes")
    })
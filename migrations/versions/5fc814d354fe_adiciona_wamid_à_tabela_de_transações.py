"""adiciona wamid à tabela de transações

Revision ID: 5fc814d354fe
Revises: 0df9482240b4
Create Date: 2024-11-20 16:42:31.494737

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5fc814d354fe"
down_revision: Union[str, None] = "0df9482240b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("transacoes", sa.Column("wamid", sa.String(), nullable=False))


def downgrade() -> None:
    op.drop_column("transacoes", "wamid")

"""remove coluna apagado transacao

Revision ID: 0df9482240b4
Revises: 63e2ab5fbd4e
Create Date: 2024-11-02 11:16:13.586327

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0df9482240b4"
down_revision: Union[str, None] = "63e2ab5fbd4e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("transacoes", "apagado")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "transacoes",
        sa.Column("apagado", sa.BOOLEAN(), autoincrement=False, nullable=True),
    )
    # ### end Alembic commands ###

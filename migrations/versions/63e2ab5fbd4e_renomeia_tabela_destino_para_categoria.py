"""renomeia tabela destino para categoria

Revision ID: 63e2ab5fbd4e
Revises: 023fdc7372f5
Create Date: 2024-10-15 22:20:40.268901

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "63e2ab5fbd4e"
down_revision: Union[str, None] = "023fdc7372f5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("transacoes", "destino", new_column_name="categoria")
    # ### end Alembic commands ###


def downgrade() -> None:
    op.alter_column("transacoes", "categoria", new_column_name="destino")
    # ### end Alembic commands ###

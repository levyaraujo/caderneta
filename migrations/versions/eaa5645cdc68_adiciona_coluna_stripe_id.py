"""adiciona coluna stripe_id

Revision ID: eaa5645cdc68
Revises: 593687b0758d
Create Date: 2024-11-27 16:33:31.399902

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "eaa5645cdc68"
down_revision: Union[str, None] = "593687b0758d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("assinaturas", sa.Column("stripe_id", sa.String(), nullable=False))
    op.create_unique_constraint(None, "assinaturas", ["stripe_id"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "assinaturas", type_="unique")
    op.drop_column("assinaturas", "stripe_id")
    # ### end Alembic commands ###

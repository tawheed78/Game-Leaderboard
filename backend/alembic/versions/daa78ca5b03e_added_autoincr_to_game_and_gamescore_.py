"""added autoincr to game and gamescore table |  migration

Revision ID: daa78ca5b03e
Revises: cd75502d420d
Create Date: 2025-02-10 02:39:49.039492

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'daa78ca5b03e'
down_revision: Union[str, None] = 'cd75502d420d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###

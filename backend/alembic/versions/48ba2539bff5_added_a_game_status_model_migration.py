"""added a game status model |  migration

Revision ID: 48ba2539bff5
Revises: ad9cdeca7420
Create Date: 2025-02-11 04:12:09.472061

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '48ba2539bff5'
down_revision: Union[str, None] = 'ad9cdeca7420'
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

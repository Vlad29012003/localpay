"""Add refresh_tokens table

Revision ID: 8cd2a455dff2
Revises: cb402f6f1257
Create Date: 2024-07-12 11:07:38.667039

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '8cd2a455dff2'
down_revision: Union[str, None] = 'cb402f6f1257'
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

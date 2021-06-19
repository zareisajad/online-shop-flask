"""add rate column

Revision ID: 7cd424f2544f
Revises: dc3d119fd655
Create Date: 2021-06-13 18:49:57.337630

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7cd424f2544f'
down_revision = 'dc3d119fd655'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('products', sa.Column('rate', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('products', 'rate')
    # ### end Alembic commands ###
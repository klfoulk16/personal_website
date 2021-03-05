"""Initial migration.

Revision ID: 7a2a4fa5ae3e
Revises: 
Create Date: 2021-03-04 11:22:29.839828

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7a2a4fa5ae3e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('admin', 'authenticated')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('admin', sa.Column('authenticated', sa.BOOLEAN(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
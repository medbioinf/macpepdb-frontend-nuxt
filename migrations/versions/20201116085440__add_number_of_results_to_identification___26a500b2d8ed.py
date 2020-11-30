"""add number_of_results to identification_projects

Revision ID: 26a500b2d8ed
Revises: 232f649b207d
Create Date: 2020-11-16 08:54:40.532524+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '26a500b2d8ed'
down_revision = '232f649b207d'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('identification_projects', sa.Column('number_of_results', sa.Integer, default=10000))


def downgrade():
    op.drop_column('identification_projects', 'number_of_results')

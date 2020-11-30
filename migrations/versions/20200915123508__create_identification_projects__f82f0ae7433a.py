"""create identification_projects

Revision ID: f82f0ae7433a
Revises: 
Create Date: 2020-09-15 12:35:08.379515+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f82f0ae7433a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'identification_projects',
        sa.Column('id', sa.BigInteger, primary_key=True),
        sa.Column('lower_precursor_tolerance', sa.Integer, nullable=False),
        sa.Column('upper_precursor_tolerance', sa.Integer, nullable=False),
        sa.Column('variable_modification_maximum', sa.Integer, nullable=False),
        sa.Column('number_of_decoys', sa.Integer, nullable=False),
        sa.Column('fragmentation_tolerance', sa.dialects.postgresql.DOUBLE_PRECISION, nullable=False),
        sa.Column('skip_search_without_targets', sa.BOOLEAN, nullable=False)
    )


def downgrade():
    os.drop_table('identification_projects')

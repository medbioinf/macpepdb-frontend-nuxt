"""create ms/ms spectra

Revision ID: d187f96b1539
Revises: f82f0ae7433a
Create Date: 2020-09-15 12:40:16.162163+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd187f96b1539'
down_revision = 'f82f0ae7433a'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'ms_ms_spectra',
        sa.Column('id', sa.BigInteger, primary_key=True),
        sa.Column('spectrum', sa.Text, nullable=False),
        sa.Column('output', sa.Text),
        sa.Column('errors', sa.Text),
        sa.Column('warnings', sa.Text),
        sa.Column('finished', sa.Boolean, default=False),
        sa.Column('finished_at', sa.BigInteger),
        sa.Column('identification_project_id', sa.BigInteger, sa.ForeignKey('identification_projects.id'), nullable=False),
    )
    op.create_index('ms_ms_spectra_identification_project_id_idx', 'ms_ms_spectra', ['identification_project_id'])

def downgrade():
    op.drop_table('ms_ms_spectra')

"""add identification metric field to ms/ms spectra and remove warning and output

Revision ID: 232f649b207d
Revises: d187f96b1539
Create Date: 2020-11-05 14:22:34.645488+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '232f649b207d'
down_revision = 'd187f96b1539'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('ms_ms_spectra', 'warnings')
    op.drop_column('ms_ms_spectra', 'output')
    op.add_column('ms_ms_spectra', sa.Column('identification_metric', sa.dialects.postgresql.JSONB, default={}))


def downgrade():
    op.drop_column('ms_ms_spectra', 'identification_metric')
    op.add_column('ms_ms_spectra', sa.Column('output', sa.Text))
    op.add_column('ms_ms_spectra', sa.Column('warnings', sa.Text))

"""rename spectrum to scan

Revision ID: b5ddaf7fa3b3
Revises: 26a500b2d8ed
Create Date: 2020-11-19 16:40:59.557507+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b5ddaf7fa3b3'
down_revision = '26a500b2d8ed'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('ms_ms_spectra', 'spectrum', new_column_name='scan')


def downgrade():
    op.alter_column('ms_ms_spectra', 'scan', new_column_name='spectrum')

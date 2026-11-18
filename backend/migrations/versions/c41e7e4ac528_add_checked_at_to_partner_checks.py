""" add checked_at to partner checks """

from alembic import op
import sqlalchemy as sa


revision = 'c41e7e4ac528'
down_revision = 'dc0a0b9e38da'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "partner_checks",
        sa.Column("checked_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("partner_checks", "checked_at")
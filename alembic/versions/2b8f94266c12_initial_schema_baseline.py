"""initial schema baseline

Revision ID: 2b8f94266c12
Revises: 
Create Date: 2026-08-01 14:19:16.376726

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2b8f94266c12'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "marcas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nombre"),
    )

    op.create_table(
        "perfumes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.Text(), nullable=False),
        sa.Column("volumen_ml", sa.Integer(), nullable=False),
        sa.Column("marca_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["marca_id"],
            ["marcas.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("perfumes")
    op.drop_table("marcas")

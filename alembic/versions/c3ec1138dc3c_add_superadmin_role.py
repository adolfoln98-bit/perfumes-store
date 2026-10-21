"""add superadmin role

Revision ID: c3ec1138dc3c
Revises: 89bee674bd17
Create Date: 2026-10-08 11:14:52.428064

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3ec1138dc3c'
down_revision: Union[str, Sequence[str], None] = '89bee674bd17'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE rol_usuario ADD VALUE 'superadmin';")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("LOCK TABLE usuarios IN ACCESS EXCLUSIVE MODE;")
    conexion = op.get_bind()
    result = conexion.execute(sa.text("SELECT EXISTS (SELECT 1 FROM usuarios WHERE rol = 'superadmin');")).scalar()

    if result:
        raise RuntimeError("Aun existen superadministradores, por favor borrelos o cambie de rol para poder continuar")

    op.execute("CREATE TYPE rol_usuario_old AS ENUM ('user', 'admin');")
    op.execute("ALTER TABLE usuarios ALTER COLUMN rol DROP DEFAULT;")
    op.execute("ALTER TABLE usuarios ALTER COLUMN rol TYPE rol_usuario_old USING rol::text::rol_usuario_old;")
    op.execute("DROP TYPE rol_usuario;")
    op.execute("ALTER TYPE rol_usuario_old RENAME TO rol_usuario;")
    op.execute("ALTER TABLE usuarios ALTER COLUMN rol SET DEFAULT 'user';")

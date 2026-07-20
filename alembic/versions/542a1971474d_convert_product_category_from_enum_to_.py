"""convert product category from enum to text

Revision ID: 542a1971474d
Revises: aa1916f478a3
Create Date: 2026-07-14 23:46:01.911040

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '542a1971474d'
down_revision: Union[str, None] = 'aa1916f478a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "products",
        "category",
        type_=sa.String(),
        postgresql_using="lower(category::text)",
    )
    op.execute("DROP TYPE productcategory")


def downgrade() -> None:
    op.execute(
        "CREATE TYPE productcategory AS ENUM "
        "('GATE', 'STAIRS', 'WINDOWS', 'SHUTTERS', 'GRILLS', 'DOORS')"
    )
    op.alter_column(
        "products",
        "category",
        type_=sa.Enum(name="productcategory"),
        postgresql_using="upper(category)::productcategory",
    )

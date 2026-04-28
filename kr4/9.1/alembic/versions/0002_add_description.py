from alembic import op
import sqlalchemy as sa


revision = "0002_add_description"
down_revision = "0001_create_products"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("products") as batch_op:
        batch_op.add_column(
            sa.Column(
                "description",
                sa.String(length=255),
                nullable=False,
                server_default="Description not set",
            )
        )


def downgrade() -> None:
    with op.batch_alter_table("products") as batch_op:
        batch_op.drop_column("description")

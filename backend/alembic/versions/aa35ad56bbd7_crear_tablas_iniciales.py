"""crear tablas iniciales

Revision ID: aa35ad56bbd7
Revises:
Create Date: 2026-05-15 19:49:30.659150
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "aa35ad56bbd7"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if not inspector.has_table("noticias"):
        op.create_table(
            "noticias",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("titulo", sa.String(length=500), nullable=False),
            sa.Column("fecha", sa.DateTime(timezone=True), nullable=True),
            sa.Column("fuente", sa.String(length=100), nullable=False),
            sa.Column("url", sa.String(length=1000), nullable=False),
            sa.Column("descripcion", sa.Text(), nullable=True),
            sa.Column("contenido", sa.Text(), nullable=True),
            sa.Column("categoria", sa.String(length=100), nullable=True),
            sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.UniqueConstraint("url", name="uq_noticia_url"),
        )
    inspector = inspect(bind)
    if "ix_noticias_id" not in _index_names(inspector, "noticias"):
        op.create_index("ix_noticias_id", "noticias", ["id"], unique=False)

    inspector = inspect(bind)
    if not inspector.has_table("cache_geocoding"):
        op.create_table(
            "cache_geocoding",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("query_original", sa.Text(), nullable=False),
            sa.Column("query_normalizada", sa.String(length=255), nullable=False),
            sa.Column("latitud", sa.Float(), nullable=False),
            sa.Column("longitud", sa.Float(), nullable=False),
            sa.Column("tipo_lugar", sa.String(length=50), nullable=False, server_default="otro"),
            sa.Column("precision", sa.String(length=50), nullable=False, server_default="baja"),
            sa.Column("proveedor", sa.String(length=50), nullable=False, server_default="nominatim"),
            sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )
    inspector = inspect(bind)
    if "ix_cache_geocoding_id" not in _index_names(inspector, "cache_geocoding"):
        op.create_index("ix_cache_geocoding_id", "cache_geocoding", ["id"], unique=False)
    if "ix_cache_geocoding_query_normalizada" not in _index_names(inspector, "cache_geocoding"):
        op.create_index(
            "ix_cache_geocoding_query_normalizada",
            "cache_geocoding",
            ["query_normalizada"],
            unique=True,
        )

    inspector = inspect(bind)
    if not inspector.has_table("ubicaciones_noticia"):
        op.create_table(
            "ubicaciones_noticia",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("noticia_id", sa.Integer(), nullable=False),
            sa.Column("texto_detectado", sa.Text(), nullable=False),
            sa.Column("lugar_normalizado", sa.String(length=255), nullable=False),
            sa.Column("tipo_lugar", sa.String(length=50), nullable=False, server_default="otro"),
            sa.Column("latitud", sa.Float(), nullable=False),
            sa.Column("longitud", sa.Float(), nullable=False),
            sa.Column("precision", sa.String(length=50), nullable=False, server_default="baja"),
            sa.Column("es_principal", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("fuente_extraccion", sa.String(length=50), nullable=False),
            sa.Column("fuente_geocodificacion", sa.String(length=50), nullable=False),
            sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.ForeignKeyConstraint(["noticia_id"], ["noticias.id"]),
            sa.UniqueConstraint(
                "noticia_id",
                "lugar_normalizado",
                "latitud",
                "longitud",
                name="uq_ubicacion_noticia_lugar_coord",
            ),
        )
    inspector = inspect(bind)
    if "ix_ubicaciones_noticia_id" not in _index_names(inspector, "ubicaciones_noticia"):
        op.create_index("ix_ubicaciones_noticia_id", "ubicaciones_noticia", ["id"], unique=False)
    if "ix_ubicaciones_noticia_noticia_id" not in _index_names(inspector, "ubicaciones_noticia"):
        op.create_index(
            "ix_ubicaciones_noticia_noticia_id",
            "ubicaciones_noticia",
            ["noticia_id"],
            unique=False,
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if "ix_ubicaciones_noticia_noticia_id" in _index_names(inspector, "ubicaciones_noticia"):
        op.drop_index("ix_ubicaciones_noticia_noticia_id", table_name="ubicaciones_noticia")
    if "ix_ubicaciones_noticia_id" in _index_names(inspector, "ubicaciones_noticia"):
        op.drop_index("ix_ubicaciones_noticia_id", table_name="ubicaciones_noticia")
    if inspector.has_table("ubicaciones_noticia"):
        op.drop_table("ubicaciones_noticia")

    inspector = inspect(bind)
    if "ix_cache_geocoding_query_normalizada" in _index_names(inspector, "cache_geocoding"):
        op.drop_index("ix_cache_geocoding_query_normalizada", table_name="cache_geocoding")
    if "ix_cache_geocoding_id" in _index_names(inspector, "cache_geocoding"):
        op.drop_index("ix_cache_geocoding_id", table_name="cache_geocoding")
    if inspector.has_table("cache_geocoding"):
        op.drop_table("cache_geocoding")

    inspector = inspect(bind)
    if "ix_noticias_id" in _index_names(inspector, "noticias"):
        op.drop_index("ix_noticias_id", table_name="noticias")
    if inspector.has_table("noticias"):
        op.drop_table("noticias")


def _index_names(inspector, table_name: str) -> set[str]:
    if not inspector.has_table(table_name):
        return set()
    return {index["name"] for index in inspector.get_indexes(table_name)}

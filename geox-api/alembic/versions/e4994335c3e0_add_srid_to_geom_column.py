"""Add srid to geom column

Revision ID: e4994335c3e0
Revises: 29413b133313
Create Date: 2022-09-19 21:48:33.581513

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e4994335c3e0'
down_revision = '29413b133313'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute("""
        ALTER TABLE shapes
        ALTER COLUMN geom
        TYPE Geometry(Geometry, 4326)
        USING ST_SetSRID(geom, 4326);
        """)
    # conn.execute("""
    #   CREATE OR REPLACE FUNCTION public.function_source(z integer, x integer, y integer, query_params json) RETURNS bytea AS $$
    #   DECLARE
    #     mvt bytea;
    #   BEGIN
    #     SELECT INTO mvt ST_AsMVT(tile, 'public.shape', 4096, 'geom', 'properties') FROM (
    #       SELECT
    #         ST_AsMVTGeom(ST_Transform(ST_CurveToLine(geom), 3857), TileBBox(z, x, y, 3857), 4096, 64, true) AS geom
    #       FROM public.shapes
    #       WHERE geom && TileBBox(z, x, y, 4326)
    #     ) as tile WHERE geom IS NOT NULL;
    #     RETURN mvt;
    #   END
    #   $$ LANGUAGE plpgsql IMMUTABLE STRICT PARALLEL SAFE;
    # """)


def downgrade() -> None:
    pass

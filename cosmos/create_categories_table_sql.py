from app.data.presets import presets, Preset
from app.core.jinja_utils import ENV, squote
import json
from itertools import islice

template = ENV.from_string(r"""
    -- generated by create_presets.py
    -- from presets.json

    DROP TABLE IF EXISTS {{ tablename }};
    CREATE TABLE IF NOT EXISTS {{ tablename }} (
        osm_id TEXT NOT NULL REFERENCES osm (id),
        category TEXT NOT NULL,
        PRIMARY KEY (osm_id, category)
    );

    {% for preset in presets %}
    INSERT INTO {{ tablename }} (osm_id, category)
    SELECT id, '{{ preset.key }}'
    FROM osm
    WHERE
    TRUE
    {%- for tag in preset.tags %}
    AND {{ tag }}
    {%- endfor %}
    AND (
        FALSE
        {%- if 'area' in preset.geometry %}
        OR (osm_type = 'W' AND geometry_type = 'POLYGON')
        {%- endif %}
        {%- if 'line' in preset.geometry %}
        OR (osm_type = 'W' AND geometry_type = 'LINESTRING')
        {%- endif %}
        {%- if 'vertex' in preset.geometry or 'point' in preset.geometry %}
        OR (osm_type = 'N')
        {%- endif %}
        {%- if 'relation' in preset.geometry %}
        OR (osm_type = 'R')
        {%- endif %}
    );
    {% endfor %}

    CREATE INDEX ON {{ tablename }} (category);
    CREATE INDEX ON {{ tablename }} (osm_id);

    """)


def _create_data(preset: Preset):
    out = {"tags": [], "geometry": preset.geometry, "key": preset.key}
    for tag, value in preset.tags.items():
        if value == "*":
            out["tags"].append("tags ? {}".format(squote(tag)))
        else:
            out["tags"].append("tags @> {} :: JSONB".format(squote(json.dumps({tag: value}))))
    return out


def main() -> None:
    tablename = "category_membership"
    data = [_create_data(preset) for preset in islice(presets.values(), None)]
    sql = template.render(tablename=tablename, presets=data)
    print(sql)

if __name__ == "__main__":
    main()
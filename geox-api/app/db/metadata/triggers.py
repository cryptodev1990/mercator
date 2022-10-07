from alembic_utils.pg_trigger import PGTrigger

__all__ = ["users_delete_trigger", "users_insert_trigger", "shapes_create_geom_trigger", "shapes_update_geom_trigger"]
entities = []

users_insert_trigger = PGTrigger(
    schema="public",
    signature="users_insert_trigger",
    on_entity="public.users",
    is_constraint=False,
    definition='AFTER INSERT ON public.users FOR EACH ROW EXECUTE FUNCTION create_default_organization()'
)
entities.append(users_insert_trigger)

shapes_create_geom_trigger = PGTrigger(
    schema="public",
    signature="shapes_create_geom_trigger",
    on_entity="public.shapes",
    is_constraint=False,
    definition='AFTER INSERT ON public.shapes FOR EACH ROW EXECUTE FUNCTION add_geom_from_geojson()'
)
entities.append(shapes_create_geom_trigger)

shapes_update_geom_trigger = PGTrigger(
    schema="public",
    signature="shapes_update_geom_trigger",
    on_entity="public.shapes",
    is_constraint=False,
    definition='AFTER UPDATE ON public.shapes FOR EACH ROW WHEN ((pg_trigger_depth() = 0)) EXECUTE FUNCTION update_geom_from_geojson()'
)
entities.append(shapes_update_geom_trigger)

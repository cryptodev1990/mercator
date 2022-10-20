# def test_create_shape(client: TestClient, alice_conn: ConnectionWithDepOverrides):
#     data = GeoShapeCreate(geojson=random_geojson())
#     with alice_conn.dep_overrides:
#         response = client.post("/geofencer/shapes", json=data.dict())
#         print(response.json())
#         assert_ok(response)
#         actual = GeoShape.parse_obj(response.json())
#         assert actual.geojson.geometry == data.geojson.geometry
#         assert actual.geojson.properties == data.geojson.properties
#     # check that it was created in the database
#     assert shape_exists(alice_conn.conn, actual.uuid)


# OLD_SHAPE =

# SHAPE_UPDATES = [
#     {"name": "This is a new name"},
#     {"properties": {"foo": 1, "bar": 2}},
#     {"geojson": random_geojson()},
#     {}
# ]

# @pytest.fixture(params=["a", "b", "c"])
# def shape_update(request):
#     return request.param


# def test_patch_shape(client: TestClient, alice_conn: ConnectionWithDepOverrides):
#     # data = shape to create
#     _ = alice_conn

#     # create a new new random shape
#     shape = create_shape(
#         _.conn,
#         user_id=_.user.id,
#         organization_id=_.organization.id,
#         geojson=random_geojson(),
#     )
#     shape_id = shape.uuid

#     # what updates are being applied
#     new_name = "This is a new name"
#     data = {"name": new_name}

#     # This is the expected result given shape + update
#     expected = copy.copy(shape)
#     shape.geojson.properties = shape.geojson.properties or {}
#     shape.geojson.properties["name"] = new_name
#     with _.dep_overrides:
#         response = client.patch(f"/geofencer/shapes/{shape_id}", json=data)
#         assert_ok(response)
#         actual = GeoShape.parse_obj(response.json())
#         assert actual.geojson == expected.geojson
#         assert actual.namespace_id == expected.namespace_id
#         assert actual.uuid == expected.uuid
#         assert actual.updated_at > expected.updated_at
#         assert actual.created_at == expected.created_at
#     # check that it was created in the database
#     assert shape_exists(_.conn, actual.uuid)

# def test_read_shape_self(
#     client: TestClient, alice_conn: ConnectionWithDepOverrides, bob: UserOrganization
# ):
#     shape = create_shape(
#         alice_conn.conn,
#         user_id=alice_conn.user.id,
#         organization_id=alice_conn.organization.id,
#         geojson=random_geojson(),
#     )
#     with alice_conn.dep_overrides:
#         response = client.get(f"/geofencer/shapes/{shape.uuid}")
#         body = response.json()
#         assert_ok(response)
#         assert GeoShape.parse_obj(body) == shape


# def test_read_shape_not_exists(
#     client: TestClient, alice_conn: ConnectionWithDepOverrides
# ):
#     # don't create any shapes
#     shape_id = uuid.uuid4()
#     with alice_conn.dep_overrides:
#         response = client.get(f"/geofencer/shapes/{shape_id}")
#         assert_status_code(response, status.HTTP_404_NOT_FOUND)


# def test_read_shape_other_user_same_org(
#     client: TestClient, alice_conn: ConnectionWithDepOverrides, bob: UserOrganization
# ):
#     shape = create_shape(
#         alice_conn.conn,
#         user_id=bob.user.id,
#         organization_id=bob.organization.id,
#         geojson=random_geojson(),
#     )
#     with alice_conn.dep_overrides:
#         response = client.get(f"/geofencer/shapes/{shape.uuid}")
#         body = response.json()
#         assert_ok(response)
#         assert GeoShape.parse_obj(body) == shape


# def test_read_shape_other_org(
#     client: TestClient, alice_conn: ConnectionWithDepOverrides, carlos: UserOrganization
# ):
#     shape = create_shape(
#         alice_conn.conn,
#         user_id=carlos.user.id,
#         organization_id=carlos.organization.id,
#         geojson=random_geojson(),
#     )
#     with alice_conn.dep_overrides:
#         response = client.get(f"/geofencer/shapes/{shape.uuid}")
#         assert_status_code(response, status.HTTP_404_NOT_FOUND)


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


# # def test_get_all_shapes(
# #     client: TestClient,
# #     alice_conn: ConnectionWithDepOverrides,
# #     carlos: UserOrganization,
# #     bob: UserOrganization,
# # ):
# #     shape = create_shape(
# #         alice_conn.conn,
# #         user_id=carlos.user.id,
# #         organization_id=carlos.organization.id,
# #         geojson=random_geojson(),
# #     )
# #     with dep_override_factory(user_id):
# #         response = client.get(f"/geofencer/shapes?user=true")
# #         assert_ok(response)
# #         body = response.json()
# #         assert body
# #         assert {shape["uuid"] for shape in body} == user_shapes


# # def test_get_all_shapes_by_organization(client, connection, dep_override_factory):
# #     user_id = 1
# #     organization_id = "5b706ffe-9608-4edd-bb00-ab9cbcb7384f"
# #     user_shapes = {
# #         "4f974f2d-572b-46f1-8741-56bf7f357d12",
# #         "8073a55a-98d4-43a7-a1fa-eefab3980f7a",
# #         "59955baf-9ffb-4c63-a6fa-6e790286d307",
# #         "88707385-829f-4edd-9860-927675a48c70",
# #         "a5da808f-b717-41cb-a566-603674172bf2",
# #         "45cd0ce9-7e2f-47cc-922a-fb02b0cf115b",
# #         "13c0b2ee-dada-421b-92eb-f756ef79d883",
# #     }

# #     with dep_override_factory(user_id):
# #         response = client.get(f"/geofencer/shapes")
# #         assert_ok(response)
# #         body = response.json()
# #         assert body
# #         assert {shape["uuid"] for shape in body} == user_shapes


# # def test_create_shape(client, connection, dep_override_factory):
# #     user_id = 1
# #     shape = GeoShapeCreate(
# #         name="fuchsia-auditor",
# #         geojson=Feature(
# #             id="1",
# #             type="Feature",
# #             geometry=Point(type="Point", coordinates=(-6.364088, -65.21654)),
# #             properties={"test": "test"},
# #         ),
# #     )

# #     uuid = None

# #     with dep_override_factory(user_id):
# #         response = client.post(f"/geofencer/shapes", json=shape.dict())
# #         assert_ok(response)
# #         body = response.json()
# #         uuid = body["uuid"]
# #         assert body
# #         assert uuid
# #         assert body["name"] == shape.name
# #         assert (
# #             tuple(body["geojson"]["geometry"]["coordinates"])
# #             == shape.geojson.geometry.dict()["coordinates"]
# #         )
# #         assert body["geojson"]["geometry"]["type"] == shape.geojson.geometry.type

# #     assert (
# #         connection.execute(
# #             text("SELECT uuid FROM shapes WHERE uuid = :uuid"), {"uuid": uuid}
# #         ).rowcount
# #         == 1
# #     )


# # def test_bulk_create_shapes(client, connection, dep_override_factory):
# #     user_id = 1
# #     shapes = [
# #         GeoShapeCreate(
# #             name="fuchsia-auditor",
# #             geojson=Feature(
# #                 id="1",
# #                 type="Feature",
# #                 properties={"test": 1},
# #                 geometry=Point(type="Point", coordinates=(-6.364088, -65.21654)),
# #             ),
# #         ),
# #         GeoShapeCreate(
# #             name="acute-vignette",
# #             geojson=Feature(
# #                 id="2",
# #                 type="Feature",
# #                 properties={"test": 1},
# #                 geometry=Point(type="Point", coordinates=(-20.586622, 53.832401)),
# #             ),
# #         ),
# #     ]

# #     with dep_override_factory(user_id):
# #         response = client.post(
# #             f"/geofencer/shapes/bulk", json=[s.dict() for s in shapes]
# #         )
# #         assert_ok(response)
# #         body = response.json()
# #         assert body
# #         assert body["num_shapes"] == 2

# #     for shp in shapes:
# #         assert (
# #             connection.execute(
# #                 text("SELECT uuid FROM shapes WHERE name = :name"),
# #                 {"name": shp.name},
# #             ).rowcount
# #             == 1
# #         )

# import time

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

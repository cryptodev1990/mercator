"""Common fixtures."""
import uuid
from functools import partial
from typing import Any, Dict, Generator, List, Literal, TypedDict, cast

import pytest
from fastapi import FastAPI
from geojson_pydantic import Polygon
from pydantic import UUID4, Field
from pytest_fastapi_deps import DependencyOverrider
from sqlalchemy import text
from sqlalchemy.engine import Connection

from app.crud.namespaces import create_namespace, get_default_namespace
from app.crud.organization import (
    add_user_to_org,
    create_organization,
    get_active_organization,
    set_active_organization,
)
from app.crud.shape import create_shape
from app.crud.user import create_user as crud_create_user
from app.crud.user import get_user_by_email
from app.dependencies import get_connection, get_current_user_org, verify_token
from app.main import app
from app.schemas import GeoShape, Namespace, Organization, User, UserOrganization
from app.schemas.organizations import Organization

from ..conftest import get_connection_override, get_current_user_org_override


def get_unused_namespace_id(conn: Connection) -> UUID4:
    """Return a shape UUID that does not exist yet."""
    ids = set(conn.execute(text("SELECT id from namespaces")).scalars())
    while (id_not_exist := uuid.uuid4()) in ids:
        pass
    return id_not_exist


def get_unused_shape_id(conn: Connection) -> UUID4:
    """Return a namespace UUID that does not exist yet."""
    ids = set(conn.execute(text("SELECT uuid from shapes")).scalars())
    while (id_not_exist := uuid.uuid4()) in ids:
        pass
    return id_not_exist


def get_user_org_by_email(conn: Connection, email: str) -> UserOrganization:
    user = get_user_by_email(conn, email)
    org = get_active_organization(conn, user.id)
    return UserOrganization(user=user, organization=org)


@pytest.fixture(scope="function")
def conn(engine) -> Generator[Connection, None, None]:
    conn = engine.connect()
    trans = conn.begin()
    try:
        yield conn
    finally:
        # This always rollsback the changes so the database state stays clean
        trans.rollback()
        conn.close()


class _UserData(TypedDict):
    name: str
    email: str
    sub_id: str
    iss: str
    namespaces: List[str]


class _OrgData(TypedDict):
    name: str
    users: List[_UserData]


ORGANIZATIONS: List[_OrgData] = [
    {
        "name": "example.com",
        "users": [
            {
                "name": "Alice",
                "email": "alice@example.com",
                "sub_id": "ehTL6xNQ8Dm2fZ380T9305fewiRJzbAz3@clients",
                "iss": "notarealissuer.example.com",
                "namespaces": ["New namespace"],
            },
            {
                "name": "Bob",
                "email": "bob@example.com",
                "sub_id": "W90rxiUvFUZBmZN6BkfFfXY8XMHmxOgd@clients",
                "iss": "notarealissuer.example.com",
                "namespaces": [],
            },
        ],
    },
    {
        "name": "example.net",
        "users": [
            {
                "name": "Carlos",
                "email": "carlos@example.net",
                "sub_id": "k7p6zN93a8NBlCjdmhCticEkIWLol74i@clients",
                "iss": "notarealissuer.example.com",
                "namespaces": [],
            }
        ],
    },
]

# Alice: 5 shapes: 3 in default, 2 non-default
# Bob: 1 shape default, 0 shape non-default - same org
# Carlos: 1 shape - diff org


class _PolygonDict(TypedDict):
    coordinates: List[List]
    type: Literal["Polygon"]


class _ShapeDict(TypedDict):
    geometry: _PolygonDict
    properties: Dict[str, Any]
    name: str
    user: str
    namespace: str


SHAPES: List[_ShapeDict] = [
    {
        "geometry": {
            "coordinates": [
                [
                    [-122.262496133, 37.811034921],
                    [-122.263324455, 37.806757455],
                    [-122.261722853, 37.804656381],
                    [-122.259848711, 37.803995272],
                    [-122.261389919, 37.801252919],
                    [-122.258969933, 37.798860828],
                    [-122.256463941, 37.799940299],
                    [-122.254298147, 37.800350458],
                    [-122.254985422, 37.80291284],
                    [-122.2521744, 37.804516549],
                    [-122.250222662, 37.804926984],
                    [-122.249757089, 37.80713043],
                    [-122.248872194, 37.808538051],
                    [-122.25195805, 37.808119482],
                    [-122.252792488, 37.807068519],
                    [-122.255966642, 37.806920538],
                    [-122.257200525, 37.80574966],
                    [-122.262496133, 37.811034921],
                ]
            ],
            "type": "Polygon",
        },
        "properties": {"description": "Lake Merritt"},
        "name": "pink-objective",
        "user": "alice",
        "namespace": "default",
    },
    {
        "geometry": {
            "coordinates": [
                [
                    [-72.285522512, 43.716927198],
                    [-72.286148631, 43.715802643],
                    [-72.28654475, 43.715182295],
                    [-72.286437623, 43.713082901],
                    [-72.285379238, 43.713181194],
                    [-72.285017246, 43.712320841],
                    [-72.284507936, 43.712108112],
                    [-72.283866447, 43.712883935],
                    [-72.282409357, 43.712326481],
                    [-72.28084594, 43.713926187],
                    [-72.28205265, 43.712092933],
                    [-72.28176267, 43.710901467],
                    [-72.280719765, 43.71001929],
                    [-72.278344642, 43.71115401],
                    [-72.273321657, 43.719210597],
                    [-72.274284142, 43.720083956],
                    [-72.275340729, 43.720534539],
                    [-72.275715912, 43.72118432],
                    [-72.276234361, 43.721383521],
                    [-72.276697084, 43.722676788],
                    [-72.275911123, 43.723766413],
                    [-72.276691522, 43.724017454],
                    [-72.278067565, 43.721503862],
                    [-72.277926412, 43.720356718],
                    [-72.277531319, 43.718673423],
                    [-72.277322315, 43.718437553],
                    [-72.27855943, 43.719399676],
                    [-72.27910413, 43.719556678],
                    [-72.279158077, 43.72066083],
                    [-72.278828943, 43.721286895],
                    [-72.280243139, 43.721441803],
                    [-72.280790508, 43.72174189],
                    [-72.280784057, 43.722135546],
                    [-72.281687366, 43.721937874],
                    [-72.282993556, 43.72103737],
                    [-72.283584194, 43.720678355],
                    [-72.285522512, 43.716927198],
                ]
            ],
            "type": "Polygon",
        },
        "properties": {
            "description": "Dartmouth cross country course",
        },
        "name": "convoluted-sledder",
        "user": "alice",
        "namespace": "default",
    },
    {
        "geometry": {
            "coordinates": [
                [
                    [-122.515244814, 37.781246929],
                    [-122.511616687, 37.766598462],
                    [-122.509408357, 37.74005562],
                    [-122.50186359, 37.700327778],
                    [-122.391264857, 37.706769931],
                    [-122.383273218, 37.719124049],
                    [-122.367910355, 37.714382741],
                    [-122.355110499, 37.726543424],
                    [-122.371791202, 37.732677917],
                    [-122.368369158, 37.740492204],
                    [-122.384421854, 37.757329145],
                    [-122.38482534, 37.772085761],
                    [-122.393790988, 37.798617967],
                    [-122.414440394, 37.807733856],
                    [-122.459787089, 37.80490674],
                    [-122.478548135, 37.808877869],
                    [-122.482144806, 37.799104771],
                    [-122.484170917, 37.794620573],
                    [-122.491664706, 37.787699188],
                    [-122.515244814, 37.781246929],
                ]
            ],
            "type": "Polygon",
        },
        "properties": {
            "description": "San Francisco",
        },
        "name": "isobaric-concentration",
        "user": "alice",
        "namespace": "new-namespace",
    },
    {
        "geometry": {
            "coordinates": [
                [
                    [-122.343100217, 37.80560894],
                    [-122.330511145, 37.799527861],
                    [-122.305669644, 37.793718925],
                    [-122.28256848, 37.794673471],
                    [-122.260454396, 37.78640294],
                    [-122.255375811, 37.789057965],
                    [-122.244875905, 37.784267294],
                    [-122.242837007, 37.778766578],
                    [-122.224547856, 37.764579488],
                    [-122.204824545, 37.741916642],
                    [-122.213319827, 37.74024589],
                    [-122.224369633, 37.747350239],
                    [-122.252518917, 37.74792417],
                    [-122.264047792, 37.744706966],
                    [-122.218908707, 37.699796655],
                    [-122.211472861, 37.700131112],
                    [-122.211003693, 37.70908193],
                    [-122.194952989, 37.713614775],
                    [-122.139759555, 37.736313994],
                    [-122.109431994, 37.749499598],
                    [-122.218926987, 37.870725404],
                    [-122.237823923, 37.862650999],
                    [-122.235548918, 37.854736875],
                    [-122.244714439, 37.853473399],
                    [-122.287960859, 37.852506984],
                    [-122.278281235, 37.828538017],
                    [-122.295362432, 37.830349946],
                    [-122.312477142, 37.828410482],
                    [-122.325853744, 37.823235523],
                    [-122.343100217, 37.80560894],
                ]
            ],
            "type": "Polygon",
        },
        "properties": {"description": "Oakland"},
        "user": "alice",
        "name": "short-bulldozer",
        "namespace": "new-namespace",
    },
    {
        "geometry": {
            "coordinates": [
                [
                    [-73.896930605, 40.891928139],
                    [-73.896129012, 40.890923571],
                    [-73.891944634, 40.890893181],
                    [-73.890981908, 40.891298292],
                    [-73.890229027, 40.892383655],
                    [-73.890211954, 40.89318306],
                    [-73.891259432, 40.893856934],
                    [-73.891790359, 40.894188667],
                    [-73.891274944, 40.895060195],
                    [-73.890770454, 40.895979008],
                    [-73.890522773, 40.896851192],
                    [-73.890007926, 40.897843837],
                    [-73.889707227, 40.898798432],
                    [-73.890521165, 40.89966132],
                    [-73.891457028, 40.899670721],
                    [-73.891025703, 40.900257699],
                    [-73.887417595, 40.902794932],
                    [-73.88774567, 40.906881636],
                    [-73.88693463, 40.908717044],
                    [-73.896707356, 40.910651484],
                    [-73.896228049, 40.904275798],
                    [-73.896375012, 40.900599152],
                    [-73.89681773, 40.897850177],
                    [-73.896077732, 40.895553975],
                    [-73.896376842, 40.893490944],
                    [-73.896930605, 40.891928139],
                ]
            ],
            "type": "Polygon",
        },
        "properties": {
            "description": "Van Cortlandt Park",
        },
        "user": "bob",
        "name": "thundering-use",
        "namespace": "default",
    },
    {
        "geometry": {
            "coordinates": [
                [
                    [-122.199135194, 37.813994432],
                    [-122.195581329, 37.810526647],
                    [-122.175517453, 37.807785198],
                    [-122.174916111, 37.810286529],
                    [-122.175519898, 37.812869206],
                    [-122.181725615, 37.818392498],
                    [-122.19152716, 37.814102899],
                    [-122.195399215, 37.813890472],
                    [-122.199135194, 37.813994432],
                ]
            ],
            "type": "Polygon",
        },
        "properties": {
            "description": "Joaquin Miller Park",
        },
        "name": "several-sword",
        "user": "carlos",
        "namespace": "default",
    },
]
"""
Random shapes generated by::

    [random_geojson().dict() for _ in range(6)]
"""


class DbExampleUser(User):
    organization: "DbExampleOrg"


class DbExampleOrg(Organization):
    users: Dict[str, DbExampleUser] = Field(default_factory=dict)
    namespaces: Dict[str, Namespace] = Field(default_factory=dict)

    @property
    def default_namespace(self) -> Namespace:
        return self.namespaces["default"]


DbExampleUser.update_forward_refs()


def create_user(
    conn: Connection, *, email: str, name: str, sub_id: str, iss: str, **kwargs
) -> User:

    user = crud_create_user(
        conn, email=email, name=name, nickname=name, sub_id=sub_id, iss=iss
    )
    return user


class ExampleDbAbc:
    def __init__(self, conn: Connection, data: List[_OrgData]) -> None:
        self.conn = conn
        self.organizations: Dict[str, DbExampleOrg] = {}
        self.shapes: Dict[str, GeoShape] = {}
        for o in data:
            org = DbExampleOrg.from_orm(
                create_organization(conn, name=cast(Dict[str, str], o)["name"])
            )
            org.namespaces["default"] = get_default_namespace(conn, org.id)
            for u in o.get("users", []):
                user = create_user(conn, **u, organization=org)  # type: ignore
                add_user_to_org(conn, user_id=user.id, organization_id=org.id)
                set_active_organization(conn, user.id, org.id)
                org.users[user.email] = DbExampleUser(**user.dict(), organization=org)
                namespaces = u.get("namespaces", [])
                if namespaces:
                    for n in namespaces:
                        namespace = create_namespace(
                            conn, name=n, user_id=user.id, organization_id=org.id
                        )
                        org.namespaces[namespace.slug] = namespace
            self.organizations[org.name] = org

    @property
    def alice(self) -> DbExampleUser:
        return self["example.com"].users["alice@example.com"]

    @property
    def bob(self) -> DbExampleUser:
        return self["example.com"].users["bob@example.com"]

    @property
    def carlos(self) -> DbExampleUser:
        return self["example.net"].users["carlos@example.net"]

    def __getitem__(self, name: str) -> DbExampleOrg:
        return self.organizations[name]

    def dep_overrides(self) -> DependencyOverrider:
        return DependencyOverrider(
            app,
            {
                get_connection: get_connection_override(self.conn),
                get_current_user_org: partial(
                    get_current_user_org_override, user_id=self.alice.id
                ),
                verify_token: lambda: {},
            },
        )

    def __enter__(self, app: FastAPI) -> DependencyOverrider:
        """Provide fastapi dependency overrides."""
        self.__dep_overrider = self.dep_overrides
        return self.__dep_overrider.__enter__()  # type: ignore

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Provide fastapi dependency overrides."""
        return self.__dep_overrider.__exit__(exc_type, exc_value, traceback)  # type: ignore


@pytest.fixture()
def db(conn: Connection) -> Generator[ExampleDbAbc, None, None]:
    # data
    # Alice shapes in default

    data = ExampleDbAbc(conn=conn, data=ORGANIZATIONS)  # types: ignore

    for shp in SHAPES:
        user: DbExampleUser = getattr(data, shp["user"])  # type: ignore
        data.shapes[shp["name"]] = create_shape(
            data.conn,
            geom=Polygon.parse_obj(shp["geometry"]),
            properties=shp["properties"],
            name=shp["name"],
            user_id=user.id,
            organization_id=user.organization.id,
            namespace_id=user.organization.namespaces[shp["namespace"]].id,
        )

    # Overrides fastapi dependencies
    with data.dep_overrides():
        yield data

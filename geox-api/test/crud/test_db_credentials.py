from test.utils import gen_cred, gen_cred_params, gen_users

from app import schemas
from app.crud.db_credentials import (
    DbCredentialModelException,
    create_conn,
    decrypt,
    encrypt,
    get_conn,
    get_conn_secrets,
    get_conns,
    get_mru_conn,
    update_conn,
)
from app.crud.organization import (
    add_user_to_organization,
    get_org,
    get_org_by_id,
    get_organization_members,
)
from app.crud.user import get_user


def test_encrypt():
    encoded = encrypt("test")
    assert decrypt(encoded.encode()) == "test"
    assert not decrypt(encrypt("testother").encode()) == "test"


def test_read_conn():
    with gen_users() as (users, db):
        user = users[0]
        new_user = get_user(db, user_id=user.id)
        assert get_org(db, new_user.id) is not None, "User should be in an organization"
        assert get_conns(db, user) == [], "User should not have any connections"

        with gen_cred(db, gen_cred_params(), by_user_id=user.id) as new_conn:
            read_conn = get_conn(db, db_credential_id=new_conn.id, user_id=user.id)
            assert read_conn
            assert new_conn
            assert get_conn_secrets(db, new_conn.id) == get_conn_secrets(
                db, read_conn.id
            )
            assert get_conns(db, user) == [read_conn]
            assert get_mru_conn(db, user.id) == read_conn

            with gen_cred(
                db, gen_cred_params(name="Other connection"), by_user_id=user.id
            ) as newer_conn:
                a = get_conn_secrets(db, new_conn.id)
                b = get_conn_secrets(db, newer_conn.id)
                assert a and b, "get_conn_secrets should return something" ""
                assert a.name and b.name
                assert a.name != b.name
                assert b.name == "Other connection"
                assert a.db_password == b.db_password
                assert [(x.id, x.name, x.created_at) for x in get_conns(db, user)][
                    0
                ] == (new_conn.id, new_conn.name, new_conn.created_at)
                assert [(x.id, x.name, x.created_at) for x in get_conns(db, user)][
                    1
                ] == (newer_conn.id, newer_conn.name, newer_conn.created_at)
                assert get_mru_conn(db, user.id) == newer_conn


def test_adversarial_read():
    with gen_users() as (users, db):
        good_user, _, bad_user, _ = users
        cred = gen_cred_params()
        with gen_cred(db, cred, by_user_id=good_user.id) as good_conn:
            assert get_org(db, bad_user.id) != get_org(
                db, good_user.id
            ), "Users should not be in the same organization"
            assert (
                get_conns(db, bad_user) == []
            ), "Adversary should not be able to see good user connections"
            assert (
                get_conns(db, good_user)[0] == good_conn
            ), "Good user should be able to see good user connections"
            try:
                get_conn(db, db_credential_id=good_conn.id, user_id=bad_user.id)
            except Exception as e:
                assert "Connection not found" in str(e)
            # Add adversary to good user's organization
            org_id = get_org(db, good_user.id)
            assert org_id
            add_user_to_organization(
                db, invited_user_id=bad_user.id, added_by_user_id=good_user.id
            )
            assert (
                get_org(db, bad_user.id) == org_id
            ), "Adverserial user should be in good user's organization"
            assert (
                get_conns(db, bad_user)[0] == good_conn
            ), "Adverserial user should be able to see good user connections"


def test_autocreate_org():
    with gen_users() as (users, db):
        user = users[3]  # User with default org
        live_user = get_user(db, user_id=user.id)
        assert live_user.name
        assert get_conns(db, user) == []
        org_id = get_org(db, user.id)
        assert org_id
        assert get_organization_members(db, org_id)[0].id == user.id
        assert get_org_by_id(db, org_id).name == live_user.name + "'s Team"

        new_cred = gen_cred_params()
        create_conn(db, new_cred, user.id)
        conn = get_conns(db, user)[0]
        assert conn.name == "Test Postgres"
        conn_secrets = get_conn_secrets(db, db_credential_id=conn.id)
        assert conn_secrets
        assert conn_secrets.db_password == "postgres"
        assert conn_secrets.db_extras == {"sslmode": "disable"}


def test_update_conn():
    with gen_users() as (users, db):
        user = users[0]
        new_cred = gen_cred_params()
        create_conn(db, new_cred, user.id)
        conn = get_conns(db, user)[0]
        assert conn.name == "Test Postgres"
        conn_secrets = get_conn_secrets(db, db_credential_id=conn.id)
        assert conn_secrets
        assert conn_secrets.db_password == "postgres"
        assert conn_secrets.db_extras == {"sslmode": "disable"}
        update_conn(
            db,
            schemas.DbCredentialUpdate(
                id=conn.id, name="Test Postgres Updated", user_id=user.id
            ),
        )
        conn = get_conns(db, user)[0]
        assert conn.name == "Test Postgres Updated"
        update_conn(
            db,
            schemas.DbCredentialUpdate(
                id=conn.id, db_password="NEWPASS", user_id=user.id
            ),
        )
        new_conn_secrets = get_conn_secrets(db, db_credential_id=conn.id)
        assert new_conn_secrets
        assert conn_secrets.db_password != new_conn_secrets.db_password


def test_same_org_read():
    with gen_users() as (users, db):
        cred = gen_cred_params()
        with gen_cred(db, cred, users[0].id) as own_conn:
            assert get_conns(db, users[0]) == [own_conn]
            assert get_conns(db, users[1]) == [own_conn]
            assert get_conns(db, users[0]) == get_conns(db, users[1])
            assert get_conns(db, users[2]) == []
            assert get_conns(db, users[3]) == []
            cred = gen_cred_params(name="Test Postgres 2", password="supersecret")
            with gen_cred(db, cred, users[2].id) as other_conn:
                test_table = [
                    (0, [own_conn]),
                    (1, [own_conn]),
                    (2, [other_conn]),
                    (3, []),
                ]
                for i, expected_conns in test_table:
                    assert get_conns(db, users[i]) == expected_conns

                # User 0 and User 1 belong to the same org
                test_table = [
                    [
                        "User 0 should be able to read his org's connections",
                        own_conn.id,
                        0,
                        own_conn.id,
                    ],
                    [
                        "User 0 should not be able to read User 2's credentials",
                        other_conn.id,
                        0,
                        None,
                    ],
                    [
                        "User 1 should be able to read that same org's connections",
                        own_conn.id,
                        1,
                        own_conn.id,
                    ],
                    [
                        "User 1 should not be able to read User 2's credentials",
                        other_conn.id,
                        1,
                        None,
                    ],
                    [
                        "User 2 should not be able to read User 1+2's org's connections",
                        own_conn.id,
                        2,
                        None,
                    ],
                    [
                        "User 2 should be able to read User 2's credentials",
                        other_conn.id,
                        2,
                        other_conn.id,
                    ],
                    [
                        "User 3 should not be able to read User 1+2's org's connections",
                        own_conn.id,
                        3,
                        None,
                    ],
                    [
                        "User 3 should not be able to read User 2's credentials",
                        other_conn.id,
                        3,
                        None,
                    ],
                ]
                for [msg, connection, user_array_idx, expected_result] in test_table:
                    user_id = users[user_array_idx].id
                    try:
                        conn = get_conn(
                            db, db_credential_id=connection, user_id=user_id
                        )
                        assert conn.id == expected_result, msg
                    except DbCredentialModelException:
                        if not expected_result:
                            assert True
                        else:
                            assert False, msg

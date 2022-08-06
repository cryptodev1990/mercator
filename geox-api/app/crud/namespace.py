from sqlalchemy.orm import Session

from app import schemas


def get_namespace_membership_by_user_id(
    db: Session, user_id: int, check_admin: bool = False
) -> set:
    """Get a set of all namespaces that a user is a member of

    If check_admin is True, only return namespaces that the user is an admin of
    """
    res = db.execute(
        """
    SELECT id
    , is_admin
    FROM namespace_members
    WHERE user_id = :user_id
    """,
        {
            "user_id": user_id,
        },
    )
    rows = res.mappings().all()
    if check_admin:
        return {row["id"] for row in rows if row["is_admin"]}
    return {row["id"] for row in rows}


def _assert_user_id_is_admin_for(db: Session, user_id: int, namespace_id: int):
    """Check that the inviter is an admin of the namespace"""
    inviter_admin_namespaces = get_namespace_membership_by_user_id(
        db, user_id, check_admin=True
    )
    assert (
        namespace_id not in inviter_admin_namespaces
    ), "User is not an admin of this namespace"


def _assert_user_id_not_member_for(db: Session, user_id: int, namespace_id: int):
    """Check that the user is not already a member of the namespace"""
    invitee_namespaces = get_namespace_membership_by_user_id(db, user_id)
    if namespace_id in invitee_namespaces:
        raise Exception("User is already a member of this namespace")


def create_namespace(
    db: Session, namespace: schemas.NamespaceCreate, user_id: int
) -> int:
    res = db.execute(
        """
    INSERT INTO namespaces (
        name,
        created_by_user_id,
        created_at,
        updated_at
    ) VALUES (
        :name,
        :created_by_user_id,
        NOW(),
        NOW()
    ) RETURNING id;
    """,
        {
            "name": namespace.name,
            "created_by_user_id": user_id,
        },
    )
    db.commit()
    rows = res.mappings().all()
    namespace_id: int = rows[0]["id"]
    return namespace_id


def create_namespace_member(
    db: Session, namespace_member: schemas.NamespaceMemberCreate, user_id: int
) -> schemas.NamespaceMember:
    """Adds a new member to a namespace.

    Inviters can only add users to a namespace that they already belong in
    and are an admin of

    Invitees cannot be added to a namespace that they are already a part of
    """

    _assert_user_id_is_admin_for(db, user_id, namespace_member.namespace_id)
    _assert_user_id_not_member_for(
        db, namespace_member.user_id, namespace_member.namespace_id
    )

    res = db.execute(
        """
    INSERT INTO namespace_members (
        user_id,
        namespace_id,
        has_read,
        has_write,
        added_by_user_id,
        is_admin,
        created_at,
        updated_at
    ) VALUES (
        :user_id,
        :namespace_id,
        :has_read,
        :has_write,
        :added_by_user_id,
        :is_admin,
        NOW(),
        NOW()
    ) RETURNING id;
    """,
        {
            "user_id": namespace_member.user_id,
            "namespace_id": namespace_member.namespace_id,
            "added_by_user_id": user_id,
            "has_read": namespace_member.has_read,
            "has_write": namespace_member.has_write,
            "is_admin": namespace_member.is_admin,
        },
    )
    rows = res.mappings().all()
    return schemas.NamespaceMember(**rows[0])


def update_namespace_member_permissions(
    db: Session, namespace_member: schemas.NamespaceMemberUpdate, user_id: int
) -> schemas.NamespaceMember:
    """Updates the permissions of a member in a namespace.

    Inviters can only update permissions of members that they are an admin of
    """

    _assert_user_id_is_admin_for(db, user_id, namespace_member.namespace_id)
    res = db.execute(
        """
    UPDATE namespace_members SET
        has_read = :has_read,
        has_write = :has_write,
        is_admin = :is_admin,
        updated_at = NOW()
    WHERE id = :id
    """,
    )
    db.commit()
    rows = res.mappings().all()
    return schemas.NamespaceMember(**rows[0])

"""CRUD functions for organizations."""
from typing import List

from pydantic import UUID4  # pylint: disable=no-name-in-module
from sqlalchemy import insert, select, text
from sqlalchemy.engine import Connection

from app.core.stats import time_db_query
from app.db.metadata import organization_members as org_mbr_tbl
from app.db.metadata import organizations as org_tbl
from app.schemas import Organization, User


class OrganizationDoesNotExistError(Exception):
    def __init__(self, id_: UUID4) -> None:
        self.id = id_

    def __str__(self) -> str:
        return f"Organization {self.id} does not exist."


class UserHasNoActiveOrganizationError(Exception):
    def __init__(self, id_: int) -> None:
        self.id = id_

    def __str__(self) -> str:
        return f"User {self.id} has no active organization."


class UserHasNoPersonalOrganizationError(Exception):
    def __init__(self, id_: int) -> None:
        self.id = id_

    def __str__(self) -> str:
        return f"User {self.id} has no personal organization."


class UserNotInOrgError(Exception):
    def __init__(self, user_id: int, organization_id: UUID4) -> None:
        self.user_id = user_id
        self.organization_id = organization_id

    def __str__(self) -> str:
        return f"User {self.user_id} is not in organization {self.organization_id}"


class UserEmailHasNoOrganizationError(Exception):
    def __init__(self, email: str) -> None:
        self.email = email

    def __str__(self) -> str:
        return f"Email {self.email} has no organization."


class StripeSubscriptionDoesNotExistError(Exception):
    def __init__(self, id_: str) -> None:
        self.id = id_

    def __str__(self) -> str:
        return f"Stripe subscription {self.id} does not exist."


def create_organization(conn: Connection, *, name: str) -> Organization:
    stmt = insert(org_tbl).returning(org_tbl)
    with time_db_query("create_organization"):
        res = conn.execute(stmt, {"name": name}).first()
    return Organization.from_orm(res)


def organization_exists(conn: Connection, organization_id: UUID4) -> bool:
    stmt = text("SELECT 1 FROM organizations WHERE id = :id")
    with time_db_query("organization_exists"):
        res = conn.execute(stmt, {"id": organization_id}).scalar()
    return bool(res)


def get_organization(conn: Connection, organization_id: UUID4) -> Organization:
    """Get an organization by id.

    Returns:
        An organization with that id. If there is no such organization,
        then ``None`` is returned. It is up to caller to handle ``None``
        values.

    """
    stmt = select(org_tbl).where(org_tbl.c.id == organization_id)  # type: ignore
    with time_db_query("get_organization"):
        res = conn.execute(stmt, {"id": organization_id}).first()
    if res is None:
        raise OrganizationDoesNotExistError(organization_id)
    return Organization.from_orm(res)


def add_user_to_org(conn: Connection, *, user_id: int, organization_id: UUID4) -> None:
    stmt = insert(org_mbr_tbl).returning(org_mbr_tbl.c.id)
    with time_db_query("add_user_to_org"):
        res = conn.execute(
            stmt, {"organization_id": organization_id, "user_id": user_id}
        ).first()
    return res.id


def is_user_in_org(conn: Connection, *, user_id: int, organization_id: UUID4) -> bool:
    stmt = text(
        "SELECT id FROM organization_members WHERE user_id = :user_id AND organization_id = :organization_id"
    )
    with time_db_query("is_user_in_org"):
        res = conn.execute(stmt, {"organization_id": organization_id, "user_id": user_id})
    return bool(res is not None)


def get_personal_org(conn: Connection, user_id: int) -> Organization:
    """Return user personal org."""
    stmt = text(
        """
        SELECT o.*
        FROM organizations AS o
        INNER JOIN organization_members AS om
        ON o.id = om.organization_id
        WHERE om.user_id = :user_id
            AND o.is_personal
            AND om.deleted_at IS NULL
        """
    )
    with time_db_query("get_personal_org"):
        res = conn.execute(stmt, {"user_id": user_id}).first()
    if res is None:
        raise UserHasNoPersonalOrganizationError(user_id)
    return Organization.from_orm(res)


def get_personal_org_id(conn: Connection, user_id: int) -> UUID4:
    """Return user personal organization id."""
    return get_personal_org(conn, user_id).id


def set_active_organization(
    conn: Connection, user_id: int, organization_id: UUID4
) -> None:
    """Set the active organization for a user.

    Args:
        conn: Database connection
        user_id: ID of the user.
        organization_id: Organization to set for the user.
    """
    if not is_user_in_org(conn, user_id=user_id, organization_id=organization_id):
        raise UserNotInOrgError(user_id, organization_id)
    stmt = text(
        """
        UPDATE organization_members
        SET active = (organization_id = :organization_id)
        WHERE user_id = :user_id
            AND deleted_at IS NULL
        """
    )
    with time_db_query("set_active_organization"):
        conn.execute(stmt, {"user_id": user_id, "organization_id": organization_id})


def get_active_org_id(conn: Connection, user_id: int) -> UUID4:
    """Get the active organization of a user.

    A user will only have one active organization at a time.

    Args:
        conn: Database connection
    """
    stmt = text(
        """
        SELECT organization_id
        FROM organization_members
        WHERE user_id = :user_id
            AND deleted_at IS NULL
            AND active
        """
    )
    with time_db_query("get_active_org_id_first"):
        res = conn.execute(stmt, {"user_id": user_id}).first()
    # Return str intead of UUID because UUID can't natively be cached in redis
    # Also this function is consistent with the return type of check_cache() if converted to str
    with time_db_query("get_active_org_id_scalar"):
        res = conn.execute(stmt, {"user_id": user_id}).scalar()
    if res is None:
        raise UserHasNoActiveOrganizationError(user_id)
    return res


def get_active_organization(conn: Connection, user_id: int) -> Organization:
    """Get the acttive organization of a user.

    A user will only have one active organization at a time.

    Returns:
        Data on the user's active org. ``None`` if no active organization is found.
        User must handle a missing active org.
    """
    stmt = text(
        """
        SELECT o.*
        FROM organization_members om
        JOIN organizations o
            ON o.id = om.organization_id
        WHERE om.user_id = :user_id
            AND om.deleted_at IS NULL
            AND om.active
        """
    )
    with time_db_query("get_active_organization"):
        res = conn.execute(stmt, {"user_id": user_id}).first()
    if res is None:
        raise UserHasNoActiveOrganizationError(user_id)
    return Organization.from_orm(res)


def add_subscription(
    conn: Connection, *, organization_id: UUID4, stripe_sub_id: str
) -> Organization:
    """Add subscription ID to organization by UUID

    Args:
        conn: Database connection
        organization_id: ID of the organization to add the subscription to.
        stripe_sub_id: Subscription to add to the organization.

    Returns:
        Organization
    """

    stmt = text(
        """
        UPDATE organizations
        SET stripe_subscription_id = :stripe_sub_id, stripe_subscription_created_at = NOW()
        WHERE id= :organization_id
        RETURNING *
        """
    )
    with time_db_query("add_subscription"):
        res = conn.execute(
            stmt, {"stripe_sub_id": stripe_sub_id, "organization_id": organization_id}
        ).first()
    return Organization.from_orm(res)


def add_stripe_customer(
    conn: Connection, *, organization_id: UUID4, stripe_customer_id: str
) -> Organization:
    """Add stripe customer ID to organization by UUID

    Args:
        conn: Database connection
        organization_id: ID of the organization to add the subscription to.
        stripe_customer_id: Customer to add to the organization.

    Returns:
        Organization
    """

    stmt = text(
        """
        UPDATE organizations
        SET stripe_customer_id = :stripe_customer_id
        WHERE id = :organization_id
        RETURNING *
        """
    )
    with time_db_query("add_stripe_customer"):
        res = conn.execute(
            stmt,
            {
                "stripe_customer_id": stripe_customer_id,
                "organization_id": organization_id,
            },
        ).first()
    return Organization.from_orm(res)


def update_payment_time(conn: Connection, *, stripe_sub_id: str) -> Organization:
    """Update payment time for subscription ID to organization by UUID

    Args:
        conn: Database connection
        organization_id: ID of the organization to add the subscription to.
        stripe_sub_id: Subscription to add to the organization.

    Returns:
        Organization
    """

    stmt = text(
        """
        UPDATE organizations
        SET stripe_paid_at=NOW()
        WHERE 1=1
          AND stripe_subscription_id = :stripe_sub_id
        RETURNING *
        """
    )
    with time_db_query("update_payment_time"):
        res = conn.execute(stmt, {"stripe_sub_id": stripe_sub_id}).first()
    return Organization.from_orm(res)


def get_all_org_members(conn: Connection, organization_id: UUID4) -> List[User]:
    """Return all members of an organization."""
    stmt = text(
        """
        SELECT u.*
        FROM users AS u
        JOIN organization_members AS om
        ON u.id=om.user_id
        WHERE 1=1
          AND om.organization_id = :organization_id
          AND om.deleted_at IS NULL
        """
    )
    with time_db_query("get_all_org_members"):
        res = conn.execute(stmt, {"organization_id": organization_id}).fetchall()
    return [User.from_orm(user) for user in res]


def create_org_member(
    conn: Connection, *, organization_id: UUID4, user_id: int, active: bool
) -> bool:
    """Add a user to an organization."""

    stmt = text(
        """
        INSERT INTO organization_members(created_at, updated_at, organization_id, user_id, active)
        VALUES(NOW(), NOW(), :organization_id, :user_id, :active)
        """
    )

    with time_db_query("create_org_member"):
        conn.execute(
            stmt,
            {"organization_id": organization_id, "user_id": user_id, "active": active},
        )

    return True


def check_if_org_member(
    conn: Connection, *, organization_id: UUID4, user_id: int
) -> bool:
    """Check if a user is a member of an organization."""

    stmt = text(
        """
        SELECT 1
        FROM organization_members
        WHERE 1=1
          AND organization_id= :organization_id
          AND user_id= :user_id
          AND deleted_at IS NULL
        """
    )

    with time_db_query("check_if_org_member"):
        res = conn.execute(
            stmt, {"organization_id": organization_id, "user_id": user_id}
        ).first()

    return res is not None


def get_org_by_subscription_id(conn: Connection, stripe_sub_id: str) -> Organization:
    """Return the organization that the user belongs to."""
    stmt = text(
        """
        SELECT *
        FROM organizations
        WHERE stripe_subscription_id= :stripe_sub_id
        """
    )
    with time_db_query("get_org_by_subscription_id"):
        res = conn.execute(stmt, {"stripe_sub_id": stripe_sub_id}).first()
    if res is None:
        raise StripeSubscriptionDoesNotExistError(stripe_sub_id)
    return Organization.from_orm(res)


def update_stripe_whitelist_status(
    conn: Connection, organization_id: UUID4, should_add=False
) -> Organization:
    """Add the organization to a whitelist where users do not have to pay for the product."""
    stmt = text(
        """
        UPDATE organizations
        SET subscription_whitelist= :should_add
        RETURNING *
        """
    )
    with time_db_query("update_stripe_whitelist_status"):
        res = conn.execute(
            stmt, {"should_add": should_add, "organization_id": organization_id}
        ).first()
    if res is None:
        raise OrganizationDoesNotExistError(organization_id)
    return Organization.from_orm(res)


def update_stripe_subscription_status(
    conn: Connection, stripe_sub_id: str, status: str
) -> Organization:
    """Update the organization's trial end date"""
    stmt = text(
        """
        UPDATE organizations
        SET stripe_subscription_status= :status
        WHERE stripe_subscription_id= :stripe_sub_id
        RETURNING *
        """
    )
    with time_db_query("update_stripe_subscription_status"):
        res = conn.execute(
            stmt, {"status": status, "stripe_sub_id": stripe_sub_id}
        ).first()
    if res is None:
        raise StripeSubscriptionDoesNotExistError(stripe_sub_id)
    return Organization.from_orm(res)

import argparse
import asyncio

from pydantic import UUID4

from app.crud.organization import (
    set_active_organization,
    get_active_organization,
    get_personal_org,
    create_org_member,
    check_if_org_member
)
from app.crud.user import get_user
from app.dependencies import get_engine, get_cache
from cli.programs.common.cli_app import CLIApp


class SwitchOrg(CLIApp):

    APP_NAME = "switch_org"

    def generate_cli(
        self, subparsers: argparse._SubParsersAction
    ) -> argparse.ArgumentParser:
        parser = subparsers.add_parser(
            self.APP_NAME,
            help="""Moves a user from one organization to another.""",
        )
        # required user name
        parser.add_argument(
            "--organization-id", help="The organization to add the user to",
            default=None,
        )
        parser.add_argument(
            '--personal-org', help="Move the user back to their personal org", action='store_true',
            default=False,
        )
        parser.add_argument(
            "--user-id",
            help="The user ID to move",
        )
        return parser

    def run(self, args, loop: asyncio.BaseEventLoop) -> None:
        if args.organization_id and args.personal_org:
            raise ValueError(
                "You can't specify an organization ID and return to personal org")
        if args.organization_id is None and not args.personal_org:
            raise ValueError(
                "At least one of organization ID or return to personal org is required")
        if args.user_id is None:
            raise ValueError("User ID is required")

        loop.run_until_complete(
            _move_user(args.organization_id, args.user_id,
                       args.personal_org)
        )


async def _move_user(organization_id: UUID4, user_id: int, return_to_personal_org: bool):
    """Connect to the database associated with your current environment and whitelist"""
    engine = await get_engine()
    with engine.begin() as conn:  # type: ignore
        if return_to_personal_org:
            org = get_personal_org(conn, user_id)
            organization_id = org.id

        active_org = None
        # if the user is already a member of the org, just set it as active
        if check_if_org_member(
                conn, organization_id=organization_id, user_id=user_id):
            print("User is already in organization, converting to active")
            set_active_organization(conn, user_id, organization_id)
        else:
            print("User is not a member of the organization")
            create_org_member(
                conn, organization_id=organization_id, user_id=user_id, active=False)
            set_active_organization(conn, user_id, organization_id)
        active_org = get_active_organization(conn, user_id)
        user = get_user(conn, user_id)
        print(
            f"Moved {user.email} ({user.id}) to {active_org.name} ({active_org.id})"
        )
    cache = get_cache()
    key = f"app:cache:user_org:{user.id}"
    if not cache:
        raise ValueError(
            "Cache connection failed - you may want to connect to the cache manually")
    if cache.get(key):
        cache.delete(key)
        print("Deleted cache entry for user organization")


switch_org_app = SwitchOrg()

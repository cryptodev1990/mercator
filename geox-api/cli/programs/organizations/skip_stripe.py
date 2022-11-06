import argparse
import asyncio

from pydantic import UUID4

from app.crud.organization import update_stripe_whitelist_status
from app.dependencies import get_engine
from cli.programs.common.cli_app import CLIApp


class SkipStripe(CLIApp):

    APP_NAME = "skip_stripe"

    def generate_cli(
        self, subparsers: argparse._SubParsersAction
    ) -> argparse.ArgumentParser:
        parser = subparsers.add_parser(
            self.APP_NAME,
            help="""
            Modify the status of an organization on our Stripe-skipping subscription whitelist. If true, we stop checking their subscription status.
            This is destructive and you should have a good reason for doing this, e.g. this is an enterprise client we're managing manually.
            """,
        )
        # required user name
        parser.add_argument(
            "--organization-id", help="The organization to add to the whitelist"
        )
        parser.add_argument(
            "--should-whitelist",
            help="Add to the whitelist (allowed values are true / false)",
        )
        return parser

    def run(self, args, loop: asyncio.BaseEventLoop) -> None:
        if args.organization_id is None:
            raise ValueError("Organization ID is required")
        if args.should_whitelist == "true":
            args.should_whitelist = True
        elif args.should_whitelist == "false":
            args.should_whitelist = False
        else:
            raise ValueError("You must be explicit about whitelist values")

        loop.run_until_complete(
            _whitelist_update(args.organization_id, args.should_whitelist)
        )


async def _whitelist_update(organization_id: UUID4, should_whitelist: bool):
    """Connect to the database associated with your current environment and whitelist"""
    engine = await get_engine()
    with engine.begin() as conn:  # type: ignore
        org = update_stripe_whitelist_status(
            conn, organization_id, should_add=should_whitelist
        )
        print(
            f"New value of {org.name} ({org.id}) for subscription whitelist: {should_whitelist}"
        )


subscription_whitelist_app = SkipStripe()

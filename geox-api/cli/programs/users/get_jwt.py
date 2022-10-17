import argparse
import asyncio
from getpass import getpass

from playwright.async_api import async_playwright

from cli.programs.common.cli_app import CLIApp


class GetJWT(CLIApp):

    APP_NAME = "get_jwt"

    def generate_cli(
        self, subparsers: argparse._SubParsersAction
    ) -> argparse.ArgumentParser:
        parser_jwt = subparsers.add_parser(
            self.APP_NAME,
            help="Get a JWT for a user. Works only if the user is already registered in Auth0 via a user name and password.",
        )
        # required user name
        parser_jwt.add_argument("--username", help="The username to get a JWT for")
        # optional password, if not provided, will prompt for it
        parser_jwt.add_argument("--password", help="Password for the user")
        parser_jwt.add_argument(
            "--use-prod", action="store_true", help="Look for the user in production"
        )
        # boolean for headless mode
        parser_jwt.add_argument(
            "--interactive",
            help="Run in interactive mode (default: False)",
            action="store_true",
            default=False,
        )
        return parser_jwt

    def run(self, args, loop: asyncio.BaseEventLoop) -> None:
        if args.username is None:
            raise ValueError("Username is required")
        if args.password is None:
            args.password = getpass()
        url = "https://mercator.tech" if args.use_prod else "http://localhost:3000"
        jwt = loop.run_until_complete(
            _get_jwt_for_user_from_auth0(
                args.username, args.password, url, not args.interactive
            )
        )
        print(jwt)


async def _get_jwt_for_user_from_auth0(username, password, url, headless=True):
    """Get a JWT for a user session from Auth0"""

    async with async_playwright() as p:
        inst = await p.chromium.launch(headless=headless)
        context = await inst.new_context()
        page = await context.new_page()
        await page.goto(url)
        await page.click("#login")
        await page.type("#username", username, delay=10)
        await page.type("#password", password, delay=10)
        await page.click('button[type="submit"]', delay=10)
        await page.wait_for_load_state("networkidle")
        # In case there is a second step to the login to authorize the app
        try:
            await page.click("text=Accept", timeout=5000)
        except:
            pass
        await page.wait_for_selector("text=Geofencer", timeout=5000)
        jwt = await page.evaluate(
            """() => {
            let jwt;
            for (const k of Object.keys(localStorage)) {
                if (k.startsWith('@@auth0')) {
                    jwt = JSON.parse(localStorage.getItem(k));
                    break;
                }
            }
            return jwt.body.id_token;
            }
        """
        )
        return jwt


get_jwt_app = GetJWT()

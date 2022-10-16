"""
CLI to manipulate shapes, users, namespaces, and other contents
of our database through the CRUD functions (though not the web API itself)

This is useful for debugging, testing, and the occasional
manual data manipulation.
"""

import argparse

from asyncio import get_event_loop
from getpass import getpass

from playwright.async_api import async_playwright
from app.core.config import get_settings


settings = get_settings()


async def get_jwt_for_user_from_auth0(username, password, url, headless=True):
    """Get a JWT for a user session from Auth0"""

    async with async_playwright() as p:
        inst = await p.chromium.launch(headless=headless)
        context = await inst.new_context()
        page = await context.new_page()
        next = await page.goto(url)
        await page.click("#login")
        await page.type("#username", username, delay=10)
        await page.type("#password", password, delay=10)
        await page.click('button[type="submit"]', delay=10)
        await page.wait_for_load_state("networkidle")
        # If there's a block with accept, click it
        try:
            await page.click("text=Accept", timeout=5000)
        except:
            pass
        # Wait for the word Mercator to appear on the page
        await page.wait_for_selector("text=Geofencer", timeout=5000)
        jwt = await page.evaluate("""() => {
            let jwt;
            for (const k of Object.keys(localStorage)) {
                if (k.startsWith('@@auth0')) {
                    jwt = JSON.parse(localStorage.getItem(k));
                    break;
                }
            }
            // create a node and set it as the body
            return jwt.body.id_token;
            }
        """)
        return jwt

"""
CLI script that takes a username and password and returns a JWT
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    subparsers.required = True

    parser_jwt = subparsers.add_parser(
        "get_jwt", help="Get a JWT for a user. Works only if the user is already registered in Auth0 via a user name and password.")
    # required user name
    parser_jwt.add_argument("--username", help="The username to get a JWT for")
    # optional password, if not provided, will prompt for it
    parser_jwt.add_argument("--password", help="Password for the user")
    parser_jwt.add_argument("--use-prod", action="store_true",
                            help="Look for the user in production")
    # boolean for headless mode
    parser_jwt.add_argument(
        "--interactive",
        help="Run in interactive mode (default: False)",
        action="store_true",
        default=False,
    )
    args = parser.parse_args()

    if parser_jwt.prog == "__init__.py get_jwt":
        if args.username is None:
            raise ValueError("Username is required")
        if args.password is None:
            args.password = getpass()
        url = "https://mercator.tech" if args.use_prod else "https://localhost:3000"
        loop = get_event_loop()
        jwt = loop.run_until_complete(
            get_jwt_for_user_from_auth0(
                args.username, args.password, url, not args.interactive)
        )
        print(jwt)

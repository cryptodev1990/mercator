"""
E2E test for the index (/) page.
"""

import pytest


def test_index_page_title(page):
    """Simple test to verify the browser tests work."""
    page.goto('/', wait_until="networkidle")
    page.wait_for_selector('.relative > .relative > .space-x-10 > div > .hover\\:underline')
    page.click('.relative > .relative > .space-x-10 > div > .hover\\:underline')
    assert page.url == 'http://localhost:3000/subscribe'
    assert page.title() == 'Mercator'

    # assert the text is on the page

    page.wait_for_selector('#checkout-and-portal-button')
    page.click('#checkout-and-portal-button')

    page.wait_for_selector('.h-full > .section > .flex > .text-2xl > .transition')
    page.click('.h-full > .section > .flex > .text-2xl > .transition')

    assert 'https://dev-w40e3mxg.us.auth0.com/u/signup?' in page.url
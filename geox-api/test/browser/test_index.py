"""
E2E test for the index (/) page.
"""

import pytest


def test_index_page_title(page):
    """Simple test to verify the browser tests work."""
    page.goto('/', wait_until="networkidle")
    assert page.title() == 'Mercator'

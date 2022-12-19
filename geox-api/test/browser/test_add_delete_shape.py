"""
E2E test for adding a shape.
"""

import pytest
import time
import os
from playwright.sync_api import expect

username = os.getenv('PLAYWRIGHT_USERNAME')
password = os.getenv('PLAYWRIGHT_PASSWORD')

def test_index_page_title(page):
    """Simple test to verify the browser tests work."""
    page.goto('/', wait_until="networkidle")
    page.wait_for_selector('.relative > .relative > .space-x-10 > div > .hover\\:underline')
    page.click('.relative > .relative > .space-x-10 > div > .hover\\:underline')
    assert page.url == 'http://localhost:3000/subscribe'
    assert page.title() == 'Mercator'

    # assert the text is on the page

    page.goto('http://localhost:3000/')

    page.wait_for_selector('#login')
    page.click('#login')

    assert 'https://dev-w40e3mxg.us.auth0.com/u/login' in page.url

    page.type('#username',username, delay=100)
    page.type('#password',password, delay=100)
    page.click('button[type="submit"]', delay=100)

    # page.wait_for_selector("text=Geofencer", timeout=5000)
    # time.sleep(1)
    # assert '/geofencer' in page.url
    page.set_viewport_size({"width": 1600, "height": 1200})

    # Look for "0 shapes in 1 folder"
    locator = page.locator('#root > div > div > div > div > div > div > footer > p')
    expect(locator).to_contain_text("0 shapes in 1 folder")

    #Select draw shape
    page.wait_for_selector('.flex:nth-child(1) > div:nth-child(2) > .bg-slate-600 > svg > path')
    page.click('.flex:nth-child(1) > div:nth-child(2) > .bg-slate-600 > svg > path')

    # Draw the shape
    time.sleep(1)
    page.mouse.click(400, 400)
    time.sleep(1)
    page.mouse.click(500, 400)
    time.sleep(1)
    page.mouse.click(500, 500)
    time.sleep(1)
    page.mouse.click(400, 500)
    time.sleep(1)
    page.mouse.click(400, 500)
    time.sleep(1)

    # Save the shape
    page.wait_for_selector('div > form > .grid > .col-span-9 > .btn:nth-child(2)')
    page.click('div > form > .grid > .col-span-9 > .btn:nth-child(2)')
    time.sleep(1)

    # Look for "1 shape in 1 folder"
    expect(locator).to_contain_text("1 shape in 1 folder")

    # CRUD metadata
    page.keyboard.down('Escape')
    page.mouse.click(450, 450)
    page.wait_for_selector('#root > div > div > div > div > div > div > div > div > div:nth-child(2) > div > div > form > div > div > button')
    page.click('#root > div > div > div > div > div > div > div > div > div:nth-child(2) > div > div > form > div > div > button')
    time.sleep(1)
    metadata_locator = page.locator('#root > div > div > div > div > div > div > div > div > div:nth-child(2) > div > div > form > div:nth-child(2) > section > input')
    page.wait_for_selector('text="Shape properties"')
    # expect(metadata_locator).to_contain_text("New Key 1")
    page.keyboard.down('Escape')

    # Copy the GeoJSON
    # Click twice to enter  edit mode
    page.mouse.click(450, 450)
    time.sleep(1)
    page.mouse.click(450, 450)
    # Select the corner, drag it, release
    time.sleep(1)
    page.mouse.move(400, 400)
    time.sleep(1)
    page.mouse.down()
    time.sleep(1)
    page.mouse.move(400, 350, steps=50)
    time.sleep(1)
    page.mouse.up()
    time.sleep(1)
    page.keyboard.down('Escape')
    # Copy the GeoJSON
    # Check if the two GeoJSONs are different

    # Select, split, save the shape
    page.mouse.click(450, 450)
    page.wait_for_selector('#root > div > div > div > div > div > div:nth-child(2) > div > div:nth-child(6) > button')
    page.click('#root > div > div > div > div > div > div:nth-child(2) > div > div:nth-child(6) > button')
    time.sleep(1)
    page.mouse.click(450,350)
    page.mouse.click(450,500)
    time.sleep(1)

    # Look for "2 shapes in 1 folder"
    page.keyboard.down('Escape')
    expect(locator).to_contain_text("2 shapes in 1 folder")

    # Select the shape and delete it
    page.mouse.click(475, 450, button='right')
    time.sleep(1)
    page.mouse.click(500, 550)
    time.sleep(1)

    page.mouse.click(425, 450, button='right')
    time.sleep(1)
    page.mouse.click(500, 550)
    time.sleep(1)

    # Look for "0 shapes in 1 folder"
    expect(locator).to_contain_text("0 shapes in 1 folder")


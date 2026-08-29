import re
import pytest
from playwright.sync_api import expect

def test_initial_page_load_and_branding(app_page):
    """Verifies that the page loads with correct branding and default Home page."""
    expect(app_page).to_have_title(re.compile(r"SpiceMart.*Indian & Mexican Groceries"))
    
    # Verify store name is displayed in header
    brand_name = app_page.locator(".store-name-text").first
    expect(brand_name).to_have_text("SpiceMart")
    
    # Home section should be visible
    expect(app_page.locator("#page-home")).to_be_visible()
    expect(app_page.locator("#page-products")).to_be_hidden()
    expect(app_page.locator("#page-contact")).to_be_hidden()
    expect(app_page.locator("#page-checkout")).to_be_hidden()

def test_desktop_navigation_links(app_page):
    """Verifies desktop navigation between Home, Products, and Contact pages."""
    # Navigate to Products
    app_page.locator("#desk-nav-products").click()
    expect(app_page.locator("#page-products")).to_be_visible()
    expect(app_page.locator("#page-home")).to_be_hidden()

    # Navigate to Contact Us
    app_page.locator("#desk-nav-contact").click()
    expect(app_page.locator("#page-contact")).to_be_visible()
    expect(app_page.locator("#page-products")).to_be_hidden()

    # Navigate back to Home
    app_page.locator("#desk-nav-home").click()
    expect(app_page.locator("#page-home")).to_be_visible()
    expect(app_page.locator("#page-contact")).to_be_hidden()

def test_brand_logo_navigates_to_home(app_page):
    """Verifies clicking the store logo returns the user to the Home page."""
    # Move to products page
    app_page.locator("#desk-nav-products").click()
    expect(app_page.locator("#page-products")).to_be_visible()

    # Click logo
    app_page.locator("header .cursor-pointer").first.click()
    expect(app_page.locator("#page-home")).to_be_visible()
    expect(app_page.locator("#page-products")).to_be_hidden()

def test_mobile_bottom_navigation_bar(app_page):
    """Verifies mobile bottom navigation buttons switch views correctly on mobile viewport."""
    app_page.set_viewport_size({"width": 390, "height": 844})
    
    # Click Products on bottom nav
    app_page.locator("#mob-nav-products").click()
    expect(app_page.locator("#page-products")).to_be_visible()
    expect(app_page.locator("#page-home")).to_be_hidden()

    # Click Contact on bottom nav
    app_page.locator("#mob-nav-contact").click()
    expect(app_page.locator("#page-contact")).to_be_visible()
    expect(app_page.locator("#page-products")).to_be_hidden()

    # Click Home on bottom nav
    app_page.locator("#mob-nav-home").click()
    expect(app_page.locator("#page-home")).to_be_visible()
    expect(app_page.locator("#page-contact")).to_be_hidden()

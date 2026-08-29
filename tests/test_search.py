import pytest
from playwright.sync_api import expect

def test_search_by_keyword(app_page):
    """Verifies that searching for keywords filters matching products and shows result banner."""
    search_input = app_page.locator("#desktop-search-input")
    search_input.fill("Cardamom")

    # Verify auto-navigation to products page
    expect(app_page.locator("#page-products")).to_be_visible()
    
    # Verify search results banner
    banner = app_page.locator("#search-results-banner")
    expect(banner).to_be_visible()
    expect(app_page.locator("#search-query-display")).to_have_text('"Cardamom"')
    expect(app_page.locator("#search-match-count")).to_have_text("1")

    # Verify filtered product
    expect(app_page.locator("text=Whole Black Cardamom").first).to_be_visible()
    expect(app_page.locator("text=Alibaba Gold Basmati Rice")).to_be_hidden()

def test_clear_search_button(app_page):
    """Verifies clearing search restores full catalog and category tabs."""
    search_input = app_page.locator("#desktop-search-input")
    search_input.fill("Rosemary")
    
    expect(app_page.locator("#search-results-banner")).to_be_visible()
    expect(app_page.locator("text=Fresh Dried Rosemary").first).to_be_visible()

    # Click Clear Search button
    app_page.locator("#search-results-banner >> text=Clear Search").click()

    # Verify banner hidden and all products restored
    expect(app_page.locator("#search-results-banner")).to_be_hidden()
    expect(search_input).to_have_value("")
    product_cards = app_page.locator("#products-grid > div")
    expect(product_cards).to_have_count(7)
    expect(app_page.locator("#category-tabs-container")).to_be_visible()

def test_search_empty_results_state(app_page):
    """Verifies searching for an unknown item displays empty state notice with recovery button."""
    search_input = app_page.locator("#desktop-search-input")
    search_input.fill("UnknownProductXYZ")
    search_input.press("Enter")

    # Empty notice should appear
    expect(app_page.locator("#empty-notice")).to_be_visible()
    expect(app_page.locator("#empty-title")).to_have_text("No matches found")

    # Click 'View All Items' recovery button
    app_page.locator("#empty-notice >> text=View All Items").click()
    expect(app_page.locator("#empty-notice")).to_be_hidden()
    product_cards = app_page.locator("#products-grid > div")
    expect(product_cards).to_have_count(7)

def test_search_triggered_from_home_page(app_page):
    """Verifies starting a search on Home page switches to Products page seamlessly."""
    expect(app_page.locator("#page-home")).to_be_visible()
    
    search_input = app_page.locator("#desktop-search-input")
    search_input.fill("Turmeric")
    search_input.press("Enter")

    expect(app_page.locator("#page-products")).to_be_visible()
    expect(app_page.locator("text=Organic Whole Turmeric").first).to_be_visible()

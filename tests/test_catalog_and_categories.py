import pytest
from playwright.sync_api import expect

def test_products_grid_renders_items(app_page):
    """Verifies that all default products render in the catalog grid."""
    app_page.locator("#desk-nav-products").click()
    
    product_cards = app_page.locator("#products-grid > div")
    expect(product_cards).to_have_count(7)
    
    # Check that prices and titles are present
    expect(app_page.locator("text=Alibaba Gold Basmati Rice").first).to_be_visible()
    expect(app_page.locator("text=Whole Black Cardamom").first).to_be_visible()
    expect(app_page.locator("text=$18.99").first).to_be_visible()

def test_category_filter_tabs(app_page):
    """Verifies filtering products by category pills on the Products page."""
    app_page.locator("#desk-nav-products").click()

    # Filter by 'Spices'
    app_page.locator("#category-tabs >> text=Spices").click()
    
    # Spices items should be visible
    expect(app_page.locator("text=Whole Black Cardamom").first).to_be_visible()
    expect(app_page.locator("text=Whole Black Peppercorns").first).to_be_visible()
    expect(app_page.locator("text=Organic Whole Turmeric").first).to_be_visible()
    
    # Rice items should NOT be visible
    expect(app_page.locator("text=Alibaba Gold Basmati Rice")).to_be_hidden()
    expect(app_page.locator("text=Roshan Royal Basmati Rice")).to_be_hidden()

    # Filter by 'Herbs & Leaves'
    app_page.locator("#category-tabs >> text=Herbs & Leaves").click()
    expect(app_page.locator("text=Kasuri Fenugreek Leaves").first).to_be_visible()
    expect(app_page.locator("text=Fresh Dried Rosemary").first).to_be_visible()
    expect(app_page.locator("text=Whole Black Cardamom")).to_be_hidden()

    # Reset to 'All Products'
    app_page.locator("#category-tabs >> text=All Products").click()
    product_cards = app_page.locator("#products-grid > div")
    expect(product_cards).to_have_count(7)

def test_home_page_category_cards_navigation(app_page):
    """Verifies that clicking category cards on Home page filters Products properly."""
    # From Home, click on Spices category card
    spices_card = app_page.locator("#home-categories-grid >> text=Spices")
    spices_card.click()

    # Should navigate to Products and filter Spices
    expect(app_page.locator("#page-products")).to_be_visible()
    expect(app_page.locator("text=Whole Black Cardamom").first).to_be_visible()
    expect(app_page.locator("text=Alibaba Gold Basmati Rice")).to_be_hidden()

def test_hero_banner_action_buttons(app_page):
    """Verifies hero banner action buttons navigate to filtered products."""
    # Test 'Explore Spices' button
    app_page.locator("text=Explore Spices").click()
    expect(app_page.locator("#page-products")).to_be_visible()
    expect(app_page.locator("text=Whole Black Cardamom").first).to_be_visible()
    expect(app_page.locator("text=Alibaba Gold Basmati Rice")).to_be_hidden()

    # Return Home and test 'Shop All Items'
    app_page.locator("#desk-nav-home").click()
    app_page.locator("text=Shop All Items").first.click()
    expect(app_page.locator("#page-products")).to_be_visible()
    product_cards = app_page.locator("#products-grid > div")
    expect(product_cards).to_have_count(7)

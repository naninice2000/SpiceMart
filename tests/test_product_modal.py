import pytest
from playwright.sync_api import expect

def test_open_and_view_product_details_modal(app_page):
    """Verifies that clicking a product opens the detail modal with correct info."""
    app_page.locator("#desk-nav-products").click()

    # Click on the Alibaba Gold Basmati Rice title
    app_page.locator("text=Alibaba Gold Basmati Rice").first.click()

    # Modal should be visible
    modal = app_page.locator("#product-modal")
    expect(modal).to_be_visible()

    # Verify modal content
    modal_content = app_page.locator("#modal-content")
    expect(modal_content.locator("h2")).to_have_text("Alibaba Gold Basmati Rice")
    expect(modal_content.locator("text=$18.99")).to_be_visible()
    expect(modal_content.locator("text=Rice & Grains")).to_be_visible()
    expect(modal_content.locator("text=Extra long grain aged basmati rice")).to_be_visible()

def test_close_modal_via_close_button(app_page):
    """Verifies closing the product modal via the top-right close button."""
    app_page.locator("#desk-nav-products").click()
    app_page.locator("text=Whole Black Cardamom").first.click()
    
    modal = app_page.locator("#product-modal")
    expect(modal).to_be_visible()

    # Click close button
    app_page.locator("#product-modal button[aria-label='Close Product Details']").click()
    expect(modal).to_be_hidden()

def test_close_modal_via_backdrop_click(app_page):
    """Verifies closing the product modal by clicking the backdrop overlay."""
    app_page.locator("#desk-nav-products").click()
    app_page.locator("text=Fresh Dried Rosemary").first.click()

    modal = app_page.locator("#product-modal")
    expect(modal).to_be_visible()

    # Click near top-left of backdrop
    modal.click(position={"x": 10, "y": 10})
    expect(modal).to_be_hidden()

def test_add_to_cart_from_inside_modal(app_page):
    """Verifies clicking Add to Cart inside product modal increments cart and closes modal."""
    app_page.locator("#desk-nav-products").click()
    app_page.locator("text=Organic Whole Turmeric").first.click()

    modal = app_page.locator("#product-modal")
    expect(modal).to_be_visible()

    # Click Add to Cart inside modal
    app_page.locator("#modal-content button:has-text('Add to Cart')").click()

    # Modal closes and cart badge updates to 1
    expect(modal).to_be_hidden()
    expect(app_page.locator("#cart-badge")).to_have_text("1")

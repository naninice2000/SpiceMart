import re
import pytest
from playwright.sync_api import expect

def test_add_product_with_custom_quantity(app_page):
    """Verifies increasing product card quantity before adding to cart."""
    app_page.locator("#desk-nav-products").click()

    # Find the Alibaba Gold Basmati Rice card (price: $18.99, id: p1)
    card = app_page.locator("#products-grid > div").first
    
    # Increase qty to 3
    plus_btn = card.locator("button[aria-label='Increase quantity']")
    plus_btn.click()
    plus_btn.click()
    expect(card.locator("#qty-p1")).to_have_text("3")

    # Add to cart
    card.locator("#add-btn-p1").click()

    # Cart badge should reflect 3 items
    expect(app_page.locator("#cart-badge")).to_have_text("3")

def test_cart_drawer_open_close(app_page):
    """Verifies opening and closing the slide-over cart drawer."""
    drawer = app_page.locator("#cart-drawer")
    backdrop = app_page.locator("#cart-drawer-backdrop")

    # Initially hidden off-screen
    expect(drawer).to_have_class(re.compile(r"translate-x-full"))

    # Open cart via header cart button
    app_page.locator("header button[aria-label='View Shopping Cart']").click()
    expect(drawer).not_to_have_class(re.compile(r"translate-x-full"))
    expect(backdrop).to_be_visible()

    # Close cart via drawer close button
    drawer.locator("button[aria-label='Close Cart']").click()
    expect(drawer).to_have_class(re.compile(r"translate-x-full"))

def test_cart_calculations_and_modifications(app_page):
    """Verifies price calculations (subtotal, tax 8.25%, total) and item quantity edits."""
    app_page.locator("#desk-nav-products").click()

    # Add 1x Alibaba Gold Basmati Rice ($18.99)
    app_page.locator("#add-btn-p1").click()

    # Add 1x Whole Black Cardamom ($6.49, id: p3)
    app_page.locator("#add-btn-p3").click()

    # Open cart drawer
    app_page.locator("header button[aria-label='View Shopping Cart']").click()

    # Expected: Subtotal = 18.99 + 6.49 = 25.48
    # Tax (8.25%) = 25.48 * 0.0825 = 2.1021 -> $2.10
    # Total = 25.48 + 2.1021 = $27.58
    expect(app_page.locator("#cart-subtotal")).to_have_text("$25.48")
    expect(app_page.locator("#cart-tax")).to_have_text("$2.10")
    expect(app_page.locator("#cart-total")).to_have_text("$27.58")

    # Increment Cardamom quantity inside drawer
    cardamom_row = app_page.locator("#cart-items > div").filter(has_text="Whole Black Cardamom")
    cardamom_row.locator("button[aria-label='Increase']").click()

    # Subtotal now: 18.99 + (6.49 * 2) = 31.97
    # Tax: 31.97 * 0.0825 = 2.6375 -> $2.64
    # Total: $34.61
    expect(app_page.locator("#cart-subtotal")).to_have_text("$31.97")
    expect(app_page.locator("#cart-tax")).to_have_text("$2.64")
    expect(app_page.locator("#cart-total")).to_have_text("$34.61")

    # Delete Rice item via trash button
    rice_row = app_page.locator("#cart-items > div").filter(has_text="Alibaba Gold Basmati Rice")
    rice_row.locator("button[aria-label='Delete item']").click()

    # Subtotal now: 6.49 * 2 = 12.98
    # Tax: 12.98 * 0.0825 = 1.07085 -> $1.07
    # Total: $14.05
    expect(app_page.locator("#cart-subtotal")).to_have_text("$12.98")
    expect(app_page.locator("#cart-tax")).to_have_text("$1.07")
    expect(app_page.locator("#cart-total")).to_have_text("$14.05")

def test_cart_state_persists_across_reload(app_page):
    """Verifies that cart items and counts survive a browser reload."""
    app_page.locator("#desk-nav-products").click()
    app_page.locator("#add-btn-p5").click() # Turmeric ($5.25)
    
    expect(app_page.locator("#cart-badge")).to_have_text("1")

    # Reload page with domcontentloaded
    app_page.reload(wait_until="domcontentloaded")
    app_page.wait_for_selector("#page-home", state="visible")

    # Badge should still be 1
    expect(app_page.locator("#cart-badge")).to_have_text("1")

    # Open cart and verify item exists
    app_page.locator("header button[aria-label='View Shopping Cart']").click()
    expect(app_page.locator("#cart-items")).to_contain_text("Organic Whole Turmeric")
    expect(app_page.locator("#cart-subtotal")).to_have_text("$5.25")

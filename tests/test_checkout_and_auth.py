import pytest
from playwright.sync_api import expect

def test_unauthenticated_checkout_blocks_order(app_page):
    """Verifies that unauthenticated users see the Google Sign-In warning on Checkout."""
    # Add product to cart
    app_page.locator("#desk-nav-products").click()
    app_page.locator("#add-btn-p1").click()

    # Go to checkout
    app_page.locator("header button[aria-label='View Shopping Cart']").click()
    app_page.locator("text=Proceed to Checkout").click()

    # Verify checkout page active
    expect(app_page.locator("#page-checkout")).to_be_visible()

    # Auth warning must be displayed
    expect(app_page.locator("#checkout-auth-warning")).to_be_visible()
    expect(app_page.locator("#checkout-auth-warning")).to_contain_text("Google Sign-In Required")

def test_authenticated_checkout_profile_display(auth_page, test_user):
    """Verifies authenticated user details are automatically populated in the checkout form."""
    # Header should display user profile info
    auth_container = auth_page.locator("#auth-container")
    expect(auth_container).to_contain_text(test_user["name"])

    # Add item and proceed to checkout
    auth_page.locator("#desk-nav-products").click()
    auth_page.locator("#add-btn-p1").click()
    auth_page.locator("header button[aria-label='View Shopping Cart']").click()
    auth_page.locator("text=Proceed to Checkout").click()

    # Check that warning is hidden and profile banner displays user data
    expect(auth_page.locator("#checkout-auth-warning")).to_be_hidden()
    expect(auth_page.locator("#checkout-display-name")).to_have_text(test_user["name"])
    expect(auth_page.locator("#checkout-display-email")).to_have_text(test_user["email"])
    expect(auth_page.locator("#cust-name-input")).to_have_value(test_user["name"])
    expect(auth_page.locator("#cust-email-input")).to_have_value(test_user["email"])

    # Check that saved physical address from Customers Sheet is auto-filled
    expect(auth_page.locator("#cust-phone-input")).to_have_value("+1 (555) 234-5678")
    expect(auth_page.locator("#cust-street-input")).to_have_value("742 Evergreen Terrace")
    expect(auth_page.locator("#cust-city-input")).to_have_value("Springfield")
    expect(auth_page.locator("#cust-state-input")).to_have_value("OR")
    expect(auth_page.locator("#cust-zip-input")).to_have_value("97477")
    expect(auth_page.locator("#address-loaded-toast")).to_be_visible()

def test_commercial_address_type_toggle_and_validation(auth_page):
    """Verifies that selecting Commercial address prompts for Business Name and validates it."""
    auth_page.locator("#desk-nav-products").click()
    auth_page.locator("#add-btn-p1").click()
    auth_page.locator("header button[aria-label='View Shopping Cart']").click()
    auth_page.locator("text=Proceed to Checkout").click()

    business_group = auth_page.locator("#business-name-group")
    expect(business_group).to_be_hidden()

    # Fill base address fields
    auth_page.locator("#cust-phone-input").fill("4155551234")
    auth_page.locator("#cust-street-input").fill("100 Market Street")
    auth_page.locator("#cust-city-input").fill("San Francisco")
    auth_page.locator("#cust-state-input").fill("CA")
    auth_page.locator("#cust-zip-input").fill("94105")

    # Select Commercial
    auth_page.locator("#cust-addr-type-input").select_option("Commercial")
    expect(business_group).to_be_visible()
    expect(auth_page.locator("#cust-business-name-input")).to_be_visible()

    # Submit without business name should show business error
    auth_page.locator("button[type='submit']:has-text('Confirm & Place Order')").click()
    expect(auth_page.locator("#business-error")).to_be_visible()
    expect(auth_page.locator("#business-error")).to_contain_text("Business / Store name is required")

    # Typing business name clears error
    auth_page.locator("#cust-business-name-input").fill("Spice Delight LLC")
    expect(auth_page.locator("#business-error")).to_be_hidden()

    # Re-select Residential
    auth_page.locator("#cust-addr-type-input").select_option("Residential")
    expect(business_group).to_be_hidden()

def test_address_field_validations(auth_page):
    """Verifies client-side validation rules for Phone, Street, City, State, and ZIP."""
    auth_page.locator("#desk-nav-products").click()
    auth_page.locator("#add-btn-p1").click()
    auth_page.locator("header button[aria-label='View Shopping Cart']").click()
    auth_page.locator("text=Proceed to Checkout").click()

    # Fill invalid data
    auth_page.locator("#cust-phone-input").fill("123")
    auth_page.locator("#cust-street-input").fill("St")
    auth_page.locator("#cust-city-input").fill("1")
    auth_page.locator("#cust-state-input").fill("X")
    auth_page.locator("#cust-zip-input").fill("941")

    # Attempt to submit
    auth_page.locator("button[type='submit']:has-text('Confirm & Place Order')").click()

    # Verify error messages are displayed
    expect(auth_page.locator("#phone-error")).to_be_visible()
    expect(auth_page.locator("#phone-error")).to_contain_text("valid 10-digit phone number")

    expect(auth_page.locator("#street-error")).to_be_visible()
    expect(auth_page.locator("#city-error")).to_be_visible()
    expect(auth_page.locator("#state-error")).to_be_visible()

    expect(auth_page.locator("#zip-error")).to_be_visible()
    expect(auth_page.locator("#zip-error")).to_contain_text("valid 5-digit US ZIP code")

    # Success modal must NOT appear
    expect(auth_page.locator("#order-success-modal")).to_be_hidden()

    # Fix inputs with valid data
    auth_page.locator("#cust-phone-input").fill("4155551234")
    expect(auth_page.locator("#phone-error")).to_be_hidden()

    auth_page.locator("#cust-street-input").fill("500 Howard Street")
    expect(auth_page.locator("#street-error")).to_be_hidden()

    auth_page.locator("#cust-city-input").fill("San Francisco")
    expect(auth_page.locator("#city-error")).to_be_hidden()

    auth_page.locator("#cust-state-input").fill("CA")
    expect(auth_page.locator("#state-error")).to_be_hidden()

    auth_page.locator("#cust-zip-input").fill("94105")
    expect(auth_page.locator("#zip-error")).to_be_hidden()

def test_complete_order_placement_flow(auth_page, test_user):
    """Verifies end-to-end order placement, invoice receipt modal, and cart cleanup with valid address."""
    # 1. Add item
    auth_page.locator("#desk-nav-products").click()
    auth_page.locator("#add-btn-p1").click() # Alibaba Rice $18.99

    # 2. Proceed to checkout
    auth_page.locator("header button[aria-label='View Shopping Cart']").click()
    auth_page.locator("text=Proceed to Checkout").click()

    # 3. Fill valid shipping information
    auth_page.locator("#cust-phone-input").fill("+1 (555) 234-5678")
    auth_page.locator("#cust-street-input").fill("742 Evergreen Terrace")
    auth_page.locator("#cust-city-input").fill("Springfield")
    auth_page.locator("#cust-state-input").fill("OR")
    auth_page.locator("#cust-zip-input").fill("97477")

    # 4. Submit Order
    auth_page.locator("button[type='submit']:has-text('Confirm & Place Order')").click()

    # 5. Verify Order Success Modal
    success_modal = auth_page.locator("#order-success-modal")
    expect(success_modal).to_be_visible()
    expect(success_modal).to_contain_text("Order Confirmed!")
    expect(success_modal).to_contain_text(test_user["name"])
    expect(success_modal).to_contain_text("742 Evergreen Terrace, Springfield, OR 97477")
    expect(success_modal).to_contain_text("ORD-")

    # 6. Verify cart is cleared
    expect(auth_page.locator("#cart-badge")).to_have_text("0")

    # 7. Click 'Back to Store' and confirm return to Home
    auth_page.locator("#order-success-modal >> text=Back to Store").click()
    expect(success_modal).to_be_hidden()
    expect(auth_page.locator("#page-home")).to_be_visible()

def test_user_logout(auth_page):
    """Verifies user can log out, clearing saved profile state."""
    auth_container = auth_page.locator("#auth-container")
    expect(auth_container).to_contain_text("Jane Doe")

    # Click logout icon button
    auth_container.locator("button[title='Sign Out']").click()

    # User profile should be gone, Sign In button appears
    expect(auth_container).to_contain_text("Sign In")

def test_new_customer_address_typing_and_google_maps_fallback(page, live_server_url):
    """Verifies that new customers not found in the sheet can manually type or use Google Maps Autocomplete."""
    from conftest import setup_page_routes
    import json

    setup_page_routes(page)
    new_user = {
        "name": "Alex Smith",
        "email": "alexsmith.new@example.com",
        "picture": "https://ui-avatars.com/api/?name=Alex+Smith&background=059669&color=fff"
    }
    page.add_init_script(f"""
        localStorage.setItem('user_google_profile', JSON.stringify({json.dumps(new_user)}));
    """)
    page.goto(f"{live_server_url}/index.html", wait_until="domcontentloaded")
    page.wait_for_selector("#page-home", state="visible")

    # Add item and go to checkout
    page.locator("#desk-nav-products").click()
    page.locator("#add-btn-p1").click()
    page.locator("header button[aria-label='View Shopping Cart']").click()
    page.locator("text=Proceed to Checkout").click()

    # Profile should show new user info, but address fields must be empty and ready for typing
    expect(page.locator("#cust-name-input")).to_have_value("Alex Smith")
    expect(page.locator("#cust-email-input")).to_have_value("alexsmith.new@example.com")
    expect(page.locator("#cust-phone-input")).to_have_value("")
    expect(page.locator("#cust-street-input")).to_have_value("")
    expect(page.locator("#cust-city-input")).to_have_value("")
    expect(page.locator("#cust-state-input")).to_have_value("")
    expect(page.locator("#cust-zip-input")).to_have_value("")
    expect(page.locator("#address-loaded-toast")).to_be_hidden()

    # Type address with validation
    page.locator("#cust-phone-input").fill("2125559876")
    page.locator("#cust-street-input").fill("100 Broadway, Suite 500")
    page.locator("#cust-city-input").fill("New York")
    page.locator("#cust-state-input").fill("NY")
    page.locator("#cust-zip-input").fill("10005")

    # Submit Order
    page.locator("button[type='submit']:has-text('Confirm & Place Order')").click()

    # Verify confirmation modal with new customer address
    success_modal = page.locator("#order-success-modal")
    expect(success_modal).to_be_visible()
    expect(success_modal).to_contain_text("Alex Smith")
    expect(success_modal).to_contain_text("100 Broadway, Suite 500, New York, NY 10005")

def test_commercial_customer_mapped_address_autofill(page, live_server_url):
    """Verifies that a returning commercial customer has business name, account type, and address auto-filled from CustomerManagement."""
    from conftest import setup_page_routes
    import json

    setup_page_routes(page)
    commercial_user = {
        "name": "Alice Watson",
        "email": "commercial@example.com",
        "picture": "https://ui-avatars.com/api/?name=Alice+Watson&background=059669&color=fff"
    }
    page.add_init_script(f"""
        localStorage.setItem('user_google_profile', JSON.stringify({json.dumps(commercial_user)}));
    """)
    page.goto(f"{live_server_url}/index.html", wait_until="domcontentloaded")
    page.wait_for_selector("#page-home", state="visible")

    # Add product and proceed to checkout
    page.locator("#desk-nav-products").click()
    page.locator("#add-btn-p1").click()
    page.locator("header button[aria-label='View Shopping Cart']").click()
    page.locator("text=Proceed to Checkout").click()

    # Verify commercial customer mapped details from mocked Apps Script
    expect(page.locator("#cust-name-input")).to_have_value("Alice Watson")
    expect(page.locator("#cust-email-input")).to_have_value("commercial@example.com")
    expect(page.locator("#cust-phone-input")).to_have_value("+1 (650) 555-1234")
    expect(page.locator("#cust-addr-type-input")).to_have_value("Commercial")
    
    # Business name input should be revealed and pre-populated
    expect(page.locator("#business-name-group")).to_be_visible()
    expect(page.locator("#cust-business-name-input")).to_have_value("Spice Gourmet Bistro LLC")

    # Physical address fields
    expect(page.locator("#cust-street-input")).to_have_value("789 Culinary Boulevard")
    expect(page.locator("#cust-city-input")).to_have_value("San Francisco")
    expect(page.locator("#cust-state-input")).to_have_value("CA")
    expect(page.locator("#cust-zip-input")).to_have_value("94103")
    expect(page.locator("#address-loaded-toast")).to_be_visible()

def test_script_error_graceful_fallback(page, live_server_url):
    """Verifies that if Apps Script returns an error or is unreachable, the form remains usable for manual entry."""
    from conftest import setup_page_routes
    import json

    setup_page_routes(page)
    error_user = {
        "name": "Error Test User",
        "email": "error@example.com",
        "picture": "https://ui-avatars.com/api/?name=Error+User&background=059669&color=fff"
    }
    page.add_init_script(f"""
        localStorage.setItem('user_google_profile', JSON.stringify({json.dumps(error_user)}));
    """)
    page.goto(f"{live_server_url}/index.html", wait_until="domcontentloaded")
    page.wait_for_selector("#page-home", state="visible")

    # Navigate to checkout
    page.locator("#desk-nav-products").click()
    page.locator("#add-btn-p1").click()
    page.locator("header button[aria-label='View Shopping Cart']").click()
    page.locator("text=Proceed to Checkout").click()

    # Form should not crash and should allow manual input
    expect(page.locator("#cust-name-input")).to_have_value("Error Test User")
    expect(page.locator("#cust-email-input")).to_have_value("error@example.com")
    expect(page.locator("#address-loaded-toast")).to_be_hidden()

    # Manual entry should work smoothly
    page.locator("#cust-phone-input").fill("4085557788")
    page.locator("#cust-street-input").fill("123 Main Street")
    page.locator("#cust-city-input").fill("San Jose")
    page.locator("#cust-state-input").fill("CA")
    page.locator("#cust-zip-input").fill("95113")

    page.locator("button[type='submit']:has-text('Confirm & Place Order')").click()
    expect(page.locator("#order-success-modal")).to_be_visible()

def test_fulfillment_option_toggle_delivery_and_pickup(page, live_server_url):
    """Verifies switching between Home Delivery and Store Pickup toggles address and scheduling containers."""
    from conftest import setup_page_routes
    import json
    from datetime import datetime, timedelta

    setup_page_routes(page)
    user = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "picture": "https://ui-avatars.com/api/?name=Jane+Doe"
    }
    page.add_init_script(f"""
        localStorage.setItem('user_google_profile', JSON.stringify({json.dumps(user)}));
    """)
    page.goto(f"{live_server_url}/index.html", wait_until="domcontentloaded")
    page.wait_for_selector("#page-home", state="visible")

    # Add item and go to checkout
    page.locator("#desk-nav-products").click()
    page.locator("#add-btn-p1").click()
    page.locator("header button[aria-label='View Shopping Cart']").click()
    page.locator("text=Proceed to Checkout").click()

    # 1. Default should be Home Delivery
    expect(page.locator("#delivery-address-container")).to_be_visible()
    expect(page.locator("#pickup-schedule-container")).to_be_hidden()

    # 2. Select Store Pickup
    page.locator("#fulfillment-pickup-label").click()
    expect(page.locator("#delivery-address-container")).to_be_hidden()
    expect(page.locator("#pickup-schedule-container")).to_be_visible()

    # Verify pickup date picker min attribute is tomorrow (>= 24 hours)
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    pickup_date_input = page.locator("#cust-pickup-date-input")
    expect(pickup_date_input).to_have_attribute("min", tomorrow)

    # 3. Switch back to Home Delivery
    page.locator("#fulfillment-delivery-label").click()
    expect(page.locator("#delivery-address-container")).to_be_visible()
    expect(page.locator("#pickup-schedule-container")).to_be_hidden()

def test_store_pickup_order_submission_flow(page, live_server_url):
    """Verifies complete Store Pickup scheduling and order submission."""
    from conftest import setup_page_routes
    import json
    from datetime import datetime, timedelta

    setup_page_routes(page)
    user = {
        "name": "David Miller",
        "email": "david@example.com",
        "picture": "https://ui-avatars.com/api/?name=David+Miller"
    }
    page.add_init_script(f"""
        localStorage.setItem('user_google_profile', JSON.stringify({json.dumps(user)}));
    """)
    page.goto(f"{live_server_url}/index.html", wait_until="domcontentloaded")
    page.wait_for_selector("#page-home", state="visible")

    # Add product and go to checkout
    page.locator("#desk-nav-products").click()
    page.locator("#add-btn-p1").click()
    page.locator("header button[aria-label='View Shopping Cart']").click()
    page.locator("text=Proceed to Checkout").click()

    # Select Store Pickup
    page.locator("#fulfillment-pickup-label").click()
    expect(page.locator("#pickup-schedule-container")).to_be_visible()
    expect(page.locator("#delivery-address-container")).to_be_hidden()

    # Attempt submit without phone, date, or time slot
    page.locator("button[type='submit']:has-text('Confirm & Place Order')").click()
    expect(page.locator("#phone-error")).to_be_visible()
    expect(page.locator("#pickup-date-error")).to_be_visible()

    # Fill phone number
    page.locator("#cust-phone-input").fill("4085551234")
    
    # 1. Test Sunday restriction: Find next Sunday
    today = datetime.now()
    days_ahead = 7 - today.isoweekday() if today.isoweekday() != 7 else 7
    next_sunday = (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
    page.locator("#cust-pickup-date-input").fill(next_sunday)
    page.locator("button[type='submit']:has-text('Confirm & Place Order')").click()
    expect(page.locator("#pickup-date-error")).to_be_visible()
    expect(page.locator("#pickup-date-error")).to_contain_text("unavailable on Sundays")

    # 2. Pick next valid weekday/Saturday (Mon-Sat)
    valid_day_offset = 1 if today.weekday() != 5 else 2 # Avoid picking Sunday
    valid_date_dt = today + timedelta(days=valid_day_offset)
    if valid_date_dt.weekday() == 6: # if Sunday
        valid_date_dt += timedelta(days=1)
    future_date = valid_date_dt.strftime("%Y-%m-%d")
    page.locator("#cust-pickup-date-input").fill(future_date)

    # Attempt submit without time slot
    page.locator("button[type='submit']:has-text('Confirm & Place Order')").click()
    expect(page.locator("#pickup-time-error")).to_be_visible()

    # Choose valid 1hr time slot in 10:00 AM - 3:00 PM range
    page.locator("#cust-pickup-time-input").select_option("1:00 PM - 2:00 PM")

    # Submit Order
    page.locator("button[type='submit']:has-text('Confirm & Place Order')").click()

    # Verify Order Success Modal reflects Store Pickup details
    success_modal = page.locator("#order-success-modal")
    expect(success_modal).to_be_visible()
    expect(success_modal).to_contain_text("David Miller")
    expect(success_modal).to_contain_text("Store Pickup")
    expect(success_modal).to_contain_text(future_date)
    expect(success_modal).to_contain_text("1:00 PM - 2:00 PM")
    expect(success_modal).to_contain_text("123 Market Street, Suite 400, San Jose, CA 95113")


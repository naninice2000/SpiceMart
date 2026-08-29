import pytest
from playwright.sync_api import expect

def test_contact_form_submission(app_page):
    """Verifies that the Contact Us form accepts user inputs and displays confirmation."""
    app_page.locator("#desk-nav-contact").click()
    expect(app_page.locator("#page-contact")).to_be_visible()

    # Fill form fields
    form = app_page.locator("#page-contact")
    form.locator("input[placeholder='John Doe']").fill("Alice Wonder")
    form.locator("input[placeholder='john@example.com']").fill("alice@example.com")
    form.locator("textarea").fill("Inquiry regarding wholesale spice delivery.")

    # Intercept browser alert dialog
    dialog_messages = []
    app_page.on("dialog", lambda dialog: (dialog_messages.append(dialog.message), dialog.accept()))

    # Click Send Message
    form.locator("button:has-text('Send Message')").click()

    # Verify dialog was triggered
    assert len(dialog_messages) == 1
    assert "Message sent successfully" in dialog_messages[0]

import pytest

playwright = pytest.importorskip("playwright")
from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:8000"


@pytest.mark.ui
def test_initial_page_load_elements_visibility(page: Page):
    """
    Test that the initial page loads correctly and essential elements
    are visible and in their expected initial states.
    """
    page.goto(BASE_URL + "/")

    # 1. Check the page title
    expect(page).to_have_title("Type Friend & Enter")

    # 2. Check the main heading "THE DOORS APPEAR LOCKED"
    main_heading = page.locator("h1#door-status")
    expect(main_heading).to_be_visible()
    expect(main_heading).to_have_text("THE DOORS APPEAR LOCKED")

    # 3. Check that the "Enter the Mines" button is initially hidden
    # It has id="protected-link" and inline style="display:none;"
    protected_button = page.locator("button#protected-link")
    expect(protected_button).to_be_hidden()

    # 4. Check for the "friend - enter" subheading
    friend_enter_subheading = page.locator("h2.runes")
    expect(friend_enter_subheading).to_be_visible()
    expect(friend_enter_subheading).to_have_text("friend - enter")

    # 5. Check that the key display area is initially hidden
    # It has id="key-display"
    key_display_area = page.locator("#key-display")
    expect(key_display_area).to_be_hidden()

    # 6. Check that the error message is initially hidden
    error_message = page.locator("#error-message")
    expect(error_message).to_be_hidden()

    # 7. Check that the mobile form is initially hidden on desktop
    mobile_form = page.locator("form#mobile-form")
    expect(mobile_form).to_be_hidden()


@pytest.mark.ui
def test_mobile_form_visible_on_mobile(playwright):
    """
    Test that the mobile form is visible when the page is loaded on a mobile device.
    """
    iphone = playwright.devices["iPhone 13 Pro"]
    browser = playwright.chromium.launch()
    context = browser.new_context(**iphone)
    page = context.new_page()
    page.goto(BASE_URL + "/")

    mobile_form = page.locator("form#mobile-form")
    expect(mobile_form).to_be_visible()

    context.close()
    browser.close()


@pytest.mark.ui
def test_mobile_form_hidden_on_desktop(page: Page):
    """
    Test that the mobile form is hidden when the page is loaded on a desktop device.
    This is also covered by test_initial_page_load_elements_visibility,
    but this test is more specific.
    """
    page.goto(BASE_URL + "/")

    mobile_form = page.locator("form#mobile-form")
    expect(mobile_form).to_be_hidden()

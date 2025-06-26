import pytest
from playwright.sync_api import Page, expect

# XXX: Skip UI tests if playwright is not installed
playwright = pytest.importorskip("playwright")

BASE_URL = "http://localhost:8000"


@pytest.mark.ui
def test_404_page_loads_on_nonexistent_route(page: Page):
    """
    Tests that navigating to a nonexistent URL serves the custom 404 page.
    """
    # XXX: Navigate to a URL that is guaranteed to not exist
    response = page.goto(f"{BASE_URL}/a-path-that-does-not-exist")

    # XXX: Check that the server responded with a 404 status code
    assert response is not None
    assert response.status == 404

    # XXX: Check for the title of the 404 page
    expect(page).to_have_title("404 - Page Not Found")

    # XXX: Check for key content on the 404 page
    heading = page.get_by_role("heading", name="404 - Page Not Found")
    expect(heading).to_be_visible()

    # XXX: Check for the user-friendly message
    message = page.get_by_text("Looks like you've taken a wrong turn in the dark mines.")
    expect(message).to_be_visible()

    # XXX: Check for the link back to the home page
    home_link = page.get_by_role("link", name="Go back to the entrance")
    expect(home_link).to_be_visible()

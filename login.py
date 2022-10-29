from config import get_password, get_username
from playwright.sync_api import Page


def login(page: Page) -> None:
    page.goto("https://sakai.unc.edu/welcome/")
    page.locator("#login_btn1 >> text=ONYEN LOGIN").click()
    assert page.url == "https://sso.unc.edu/idp/profile/SAML2/Redirect/SSO?execution=e1s1"

    page.locator("input[type=\"text\"]").fill(get_username())
    page.locator("text=Loading... Next").click()
    page.locator("input[name=\"j_password\"]").fill(get_password())

    # Click text=Sign in
    with page.expect_navigation(url="https://sakai.unc.edu/portal"):
        page.locator("text=Loading... Sign in").click()

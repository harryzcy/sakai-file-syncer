from config import get_password, get_username
from playwright.sync_api import Page


def login(page: Page) -> None:
    page.goto("https://sakai.unc.edu/welcome/")
    page.click("text=onyen login")
    assert page.url == "https://sso.unc.edu/idp/profile/SAML2/Redirect/SSO?execution=e1s1"

    page.fill("input[id=\"username\"]", get_username())
    page.fill("input[id=\"password\"]", get_password())

    # Click text=Sign in
    with page.expect_navigation(url="https://sakai.unc.edu/portal"):
        page.click("text=Sign in")

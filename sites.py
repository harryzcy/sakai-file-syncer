from typing import Iterable
from playwright.sync_api import Page

from resources import Resources
import config


class Site:
    def __init__(self, page: Page, id: str, title: str) -> None:
        self.__id = id
        self.__title = title
        self.__page = page
        self.__resources = Resources(page)

    @property
    def id(self) -> str:
        """Returns site id."""
        return self.__id

    @property
    def title(self) -> str:
        """Returns site title."""
        return self.__title

    def goto(self):
        """Navigates to the site."""

        assert "sakai.unc.edu/portal" in self.__page.url

        el = self.__page.query_selector(f"a[title=\"{self.title}\"]")
        if not el:
            return

        with self.__page.expect_navigation():
            el.click()

    def goto_site_resources(self):
        """Navigate to the Resources tab of this site."""

        self.goto()

        current_menuitem = self.__page.query_selector(
            "#toolMenu li.is-current .Mrphs-toolsNav__menuitem--title")
        if current_menuitem.inner_text == "Resources":
            return

        resources_el = self.__page.query_selector(
            "#toolMenu li a:has-text('Resources')")
        with self.__page.expect_navigation():
            resources_el.click()

    @property
    def resources(self):
        """Returns Resources object."""
        return self.__resources


def get_sites(page: Page) -> Iterable[Site]:
    sites = page.query_selector_all("#topnav_container li a.link-container")
    for site in sites:
        href = site.get_attribute("href")
        id = href.split("/")[-1]
        title = site.get_attribute("title")
        yield Site(page, id, title)


def get_course_sites(page: Page) -> Iterable[Site]:
    sites = get_sites(page)
    return [site for site in sites if config.get_current_term() in site.title]

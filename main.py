import os
import sys
from playwright.sync_api import Playwright, Page, sync_playwright
from resources import Resources
from sites import get_course_sites
from login import login
import downloader
import config


def start(playwright: Playwright, debug=False) -> Page:
    browser = playwright.chromium.launch(headless=not debug)
    context = browser.new_context()

    page = context.new_page()

    return page


def finish(page: Page):
    page.close()
    page.context.close()
    page.context.browser.close()


def main(debug=False):
    with sync_playwright() as p:
        page = start(p, debug=debug)

        login(page)
        for site in get_course_sites(page):
            if not config.get_site_enable(site.title):
                continue

            site.goto_site_resources()
            site.resources.expand_all_folders()
            root = site.resources.get_root_resource()
            root.root_path = config.get_download_directory(site.title)

            for resource in Resources.walk(site.title, root):
                downloader.sync(page.context, resource)

        finish(page)


if __name__ == "__main__":
    # python version at least 3.10
    assert sys.version_info.major == 3
    assert sys.version_info.minor >= 10

    debug_env = os.getenv("DEBUG")
    debug = debug_env == 'true' if debug_env else False

    config.init()
    main(debug=debug)

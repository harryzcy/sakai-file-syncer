from pathlib import Path, PurePath
import re
from playwright.sync_api import Page, ElementHandle

import config

text_indent_regex = re.compile(r"text-indent: ?([0-9]+)em", re.IGNORECASE)


def get_text_indent(style: str) -> int:
    """Get text-indent from css inline style"""
    m = text_indent_regex.search(style)
    return int(m.group(1))


class Resource:
    def __init__(self, tr: ElementHandle) -> None:
        title_td = tr.query_selector("td.title")

        self.__title = title_td.query_selector(
            "span.resource-name"
        ).inner_text()
        # title <a> element
        title_a_el = title_td.query_selector("a:last-of-type")
        self.__link = title_a_el.get_attribute("href")
        self.__filetype = title_a_el.get_attribute("title")
        self.__indent = get_text_indent(title_td.get_attribute("style"))

        self.__parent: Resource = None
        self.__children = []

        self.__root_path = ""

        if self.__indent == 0:  # skip for root resource
            self.__creator = None
            self.__modified_time = None
            self.__item_num = -1
            self.__size = 0
            return

        self.__creator = tr.query_selector(".resource-creator").inner_text()
        self.__modified_time = tr.query_selector(
            ".resource-modified").inner_text()
        size = tr.query_selector(".resource-size").inner_text()
        if "item" in size.lower():
            # folder type
            self.__item_num = int(size.split(" ")[0])
            self.__size = 0
        else:
            # file type
            self.__item_num = -1
            self.__size = size

    @property
    def title(self):
        return self.__title

    @property
    def link(self):
        return self.__link

    @property
    def filetype(self):
        return self.__filetype

    @property
    def indent(self):
        return self.__indent

    @property
    def parent(self):
        return self.__parent

    @property
    def children(self):
        return self.__children

    @property
    def creator(self):
        return self.__creator

    @property
    def modified_time(self):
        return self.__modified_time

    @property
    def item_num(self):
        return self.__item_num

    @property
    def size(self):
        return self.__size

    @property
    def root_path(self):
        return self.__root_path

    @parent.setter
    def parent(self, value):
        self.__parent = value

    @root_path.setter
    def root_path(self, value: str):
        self.__root_path = value

    @property
    def local_directory(self):
        if self.__parent is None:
            # is root if parent is None
            return self.__root_path
        dir = PurePath(self.parent.local_directory)
        if self.__filetype == 'Folder':
            dir = dir.joinpath(self.title)
        return dir

    def add_children(self, child):
        self.__children.append(child)
        child.parent = self


class Resources:

    def __init__(self, page: Page) -> None:
        self.__page = page

    def ensure_currect_menu(self):
        a_el = self.__page.query_selector("#toolMenu > ul > li.is-current > a")
        assert a_el
        assert a_el.get_attribute("title") == "Resources"

    @property
    def current_path(self):
        self.ensure_currect_menu()

        li_els = self.__page.query_selector_all(
            "#showForm ol li:not(.dropdown)")

        path = []
        for li in li_els:
            path.append(li.inner_text().strip())
        return path

    def expand_all_folders(self):
        while True:
            self.__page.wait_for_selector("table.resourcesList")
            el = self.__page.query_selector(
                "table.resourcesList a.nil.fa-folder")
            if not el:
                break
            with self.__page.expect_navigation():
                el.click()

    def get_root_resource(self):
        """Syncs all resources from sakai with the local filesystem"""

        indent_list: list[Resource] = []

        self.__page.wait_for_selector("table.resourcesList")
        trs = self.__page.query_selector_all("table.resourcesList tbody > tr")
        for tr in trs:
            if tr.query_selector("#expansion"):
                continue

            resource = Resource(tr)
            update_indent_list(indent_list, resource)
            if len(indent_list) > 1:
                indent_list[-2].add_children(resource)

        return indent_list[0]

    @staticmethod
    def walk(site_name: str, resource: Resource):
        directory = str(Path(resource.local_directory).expanduser())
        if directory not in config.get_skip_directories(site_name):
            yield resource
            for child in resource.children:
                yield from Resources.walk(site_name, child)


def update_indent_list(indent_list: list[Resource], resource: Resource):
    indent = resource.indent
    while indent < len(indent_list):
        indent_list.pop()
    indent_list.append(resource)

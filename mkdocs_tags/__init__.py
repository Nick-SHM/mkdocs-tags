# Copyright 2020 Nick Shu <nick.shm.shu.git@outlook.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""An MkDocs plugin for tags support

This plugin reads tag info from the metadata section of each page, generate a
list of tags on each page, and generate a tag page with a list of all tags and
the pages under each of them.

Not intended for direct import.
"""

from __future__ import annotations

import copy
import operator
from os import path
from typing import Dict, List
from xml.etree import ElementTree

import jinja2
import markdown
from mkdocs import config, plugins
from mkdocs.structure import files, nav, pages

_TAGS_META_ENTRY = "tags"
_ON_PAGE_TMPLT_CFG_ENTRY = "on_page_tmplt"
_ON_PAGE_TMPLT_PATH_CFG_ENTRY = "on_page_tmplt_path"
_TAG_PAGE_TMPLT_CFG_ENTRY = "tag_page_tmplt"
_TAG_PAGE_TMPLT_PATH_CFG_ENTRY = "tag_page_tmplt_path"
_TAG_PAGE_MD_PATH_CFG_ENTRY = "tag_page_md_path"

_DFT_TAG_PAGE_MD_PATH = "tags.md"
_DFT_TAG_PAGE_TMPLT = """# {{page.title}}
{% for tag in pages_under_tag %}
## {{tag.name}}
{% for page_info in pages_under_tag[tag] %}
* [{{ page_info.title }}]({{ page_info.rel_path }})
{% endfor %}
{% endfor %}
"""
_DFT_ON_PAGE_TMPLT = """{% set links = [] %}
{% for tag in tags %}
{{ links.append('[' + tag.name + '](' + tag_page_md_rel_path +
    '#' + tag.header_id + ')') or "" }}
{% endfor %}

{{ markdown }}
{% if tags %}
---
Tags: **{{ links | join('**, **')}}**
{% endif %}
"""


class _TagInfo:
    """Stores infomation about a tag.

    Attributes:
        name: the name of the tag
        header_id: the HTML id of the section of the tag in the tag page. It
          will be set in `_set_header_ids()`
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.header_id = ""  # to be set in `_set_header_ids()`

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, _TagInfo):
            return NotImplemented
        return self.name == other.name

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class _PageInfo:
    """Stores infomation about a page.

    Attributes:
        title: title of the page
        abs_path: absolute path to the page
        rel_path: path to the page relative to the tag page
        tags: a `List[_TagInfo]` of tags of the page
    """

    def __init__(self, page: pages.Page, tag_page_md_path: str) -> None:
        self.title: str = page.title
        self.abs_path: str = page.file.src_path
        self.rel_path = path.relpath(
            path=self.abs_path, start=path.dirname(tag_page_md_path)
        )
        self.tags: List[_TagInfo] = []
        # to be set in `_collect_tags_and_pages_info()`


class MkDocsTags(plugins.BasePlugin):  # type: ignore
    # silence mypy error: Class cannot subclass 'BasePlugin' (has type 'Any')
    """An MkDocs plugin for tags support

    Attributes:
        config_scheme: see base class
    """

    config_scheme = (
        (
            _TAG_PAGE_TMPLT_CFG_ENTRY,
            config.config_options.Type(str, default=_DFT_TAG_PAGE_TMPLT),
        ),
        (
            _TAG_PAGE_TMPLT_PATH_CFG_ENTRY,
            config.config_options.Type(str, default=""),
        ),
        (
            _ON_PAGE_TMPLT_CFG_ENTRY,
            config.config_options.Type(str, default=_DFT_ON_PAGE_TMPLT),
        ),
        (
            _ON_PAGE_TMPLT_PATH_CFG_ENTRY,
            config.config_options.Type(str, default=""),
        ),
        (
            _TAG_PAGE_MD_PATH_CFG_ENTRY,
            config.config_options.Type(str, default=_DFT_TAG_PAGE_MD_PATH),
        ),
    )

    def __init__(self) -> None:
        self._pages_under_tag: Dict[_TagInfo, List[_PageInfo]] = {}
        self._page_info_of_abs_path: Dict[str, _PageInfo] = {}
        self._tag_info_of_name: Dict[str, _TagInfo] = {}
        self._tag_page_md_path = ""
        self._tag_page_tmplt = ""
        self._on_page_tmplt = ""

    def on_config(self, config: config.Config) -> config.Config:
        """Determines the templates from the config.

        See base class for argument and return value info.
        """
        # Read the path of the markdown file of the tag page
        self._tag_page_md_path = self.config[_TAG_PAGE_MD_PATH_CFG_ENTRY]
        # Read the template of the tag page
        tag_page_tmplt_path = self.config[_TAG_PAGE_TMPLT_PATH_CFG_ENTRY]
        docs_dir = config["docs_dir"]
        if tag_page_tmplt_path == "":
            self._tag_page_tmplt = self.config[_TAG_PAGE_TMPLT_CFG_ENTRY]
        else:
            with open(path.join(docs_dir, tag_page_tmplt_path)) as file:
                self._tag_page_tmplt = file.read()
        # Read the template of on-page tag lists
        on_page_tmplt_path = self.config[_ON_PAGE_TMPLT_PATH_CFG_ENTRY]
        if on_page_tmplt_path == "":
            self._on_page_tmplt = self.config[_ON_PAGE_TMPLT_CFG_ENTRY]
        else:
            with open(path.join(docs_dir, on_page_tmplt_path)) as file:
                self._on_page_tmplt = file.read()
        return config

    def _collect_tags_and_pages_info(
        self, nav: nav.Navigation, config: config.Config
    ) -> str:
        """Collects unsorted tags and pages info from markdown files.

        Args:
            nav: the `mkdocs.structure.nav.Navigation` instance of the site
            config: the `mkdocs.config.Config` instance of the site

        Returns:
            a str containing title of the tag page, to be used in
            `_set_header_ids()`
        """
        config_copy = copy.copy(config)
        config_copy["plugins"] = plugins.PluginCollection()
        # Remove plugins in `config`. Otherwise,
        # `page_copy.read_source()` will call `on_page_read_source()`
        # for each plugin
        for page in nav.pages:
            page_copy = copy.copy(page)
            page_copy.read_source(config_copy)  # Read meta data
            # Collect the title of the tag page
            if page_copy.file.src_path == self._tag_page_md_path:
                tag_page_title: str = page_copy.title
            # Collect tag and page info
            page_info = _PageInfo(
                page=page_copy, tag_page_md_path=self._tag_page_md_path
            )
            self._page_info_of_abs_path[page_info.abs_path] = page_info
            if _TAGS_META_ENTRY not in page_copy.meta:
                continue
            tag_names = page_copy.meta[_TAGS_META_ENTRY]
            if not isinstance(tag_names, list):
                continue
            for tag_name in tag_names:
                if not isinstance(tag_name, str):
                    continue
                if tag_name in self._tag_info_of_name:
                    tag = self._tag_info_of_name[tag_name]
                else:
                    tag = _TagInfo(name=tag_name)
                    self._tag_info_of_name[tag_name] = tag
                page_info.tags.append(tag)
                if tag not in self._pages_under_tag:
                    self._pages_under_tag[tag] = []
                self._pages_under_tag[tag].append(page_info)
        return tag_page_title

    def _sort_tags_and_pages(self) -> None:
        """Sorts the tags and pages info by their names and titles."""
        for tag in self._pages_under_tag:
            self._pages_under_tag[tag].sort(key=operator.attrgetter("title"))
        self._pages_under_tag = {
            tag: self._pages_under_tag[tag]
            for tag in sorted(
                self._pages_under_tag, key=operator.attrgetter("name")
            )
        }

    def _set_header_ids(self, tag_page_title: str) -> None:
        """Sets the header ids of the tags on the tags page.

        Precondition: `self._tags_and_pages` has been sorted.

        This function sets header ids by rendering a mock tag page using
        Python-Markdown search for the ids by the headers
        """
        # Generate a mock markdown file for the tags page
        md = "# " + tag_page_title + "\n\n"
        for tag in self._pages_under_tag:
            md += "## " + tag.name + "\n\n"
        # Render HTML using Python-Markdown
        html = markdown.markdown(md, extensions=["toc"])
        # Parse HTML. A tag is added as root to make it valid XML.
        root = ElementTree.fromstring("<data>" + html + "</data>")
        # Search for headers and their ids
        tag_names_and_ids: Dict[str, str] = {}
        for child in root:
            if child.tag == "h2":
                if isinstance(child.text, str):
                    tag_names_and_ids[child.text] = child.attrib.get("id", "")
        for tag in self._pages_under_tag:
            tag.header_id = tag_names_and_ids[tag.name]

    def on_nav(
        self, nav: nav.Navigation, config: config.Config, files: files.Files,
    ) -> nav.Navigation:
        """Reads tag and title info into `self._pages_under_tag`.

        See base class for argument and return value info.
        """
        tag_page_title = self._collect_tags_and_pages_info(
            nav=nav, config=config
        )
        self._sort_tags_and_pages()
        self._set_header_ids(tag_page_title=tag_page_title)
        return nav

    def on_page_markdown(
        self,
        markdown: str,
        page: pages.Page,
        config: config.Config,
        files: files.Files,
    ) -> str:
        """Generates on-page tag lists and the tag page.

        See base class for argument and return value info.
        """
        # Generate the tag page
        md_abs_path = page.file.src_path
        if md_abs_path == self._tag_page_md_path:
            jinja_tmplt = jinja2.Template(self._tag_page_tmplt)
            markdown = jinja_tmplt.render(
                pages_under_tag=self._pages_under_tag,
                markdown=markdown,
                page=page,
                config=config,
            )
        # Generate on-page tag lists
        jinja_tmplt = jinja2.Template(self._on_page_tmplt)
        tag_page_md_rel_path = path.relpath(
            path=self._tag_page_md_path, start=path.dirname(md_abs_path)
        )
        markdown = jinja_tmplt.render(
            tags=self._page_info_of_abs_path[md_abs_path].tags,
            markdown=markdown,
            page=page,
            config=config,
            tag_page_md_rel_path=tag_page_md_rel_path,
        )
        return markdown

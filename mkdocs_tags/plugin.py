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

This plugin reads tag info from the metadata section of each page,
generate a list of tags on each page, and generate a tag page with a
list of all tags and the pages under each of them.

Not intended for direct import.
"""

from __future__ import annotations

import copy
import jinja2
import operator
from mkdocs import config
from mkdocs.structure import files
from mkdocs.structure import nav
from mkdocs.structure import pages
from mkdocs import plugins
from os import path
from typing import Dict, List

_TAGS_META_ENTRY = "tags"
_ON_PAGE_TMPLT_CFG_ENTRY = "on_page_tmplt"
_ON_PAGE_TMPLT_PATH_CFG_ENTRY = "on_page_tmplt_path"
_TAG_PAGE_TMPLT_CFG_ENTRY = "tag_page_tmplt"
_TAG_PAGE_TMPLT_PATH_CFG_ENTRY = "tag_page_tmplt_path"
_TAG_PAGE_MD_PATH_CFG_ENTRY = "tag_page_md_path"

_DFT_TAG_PAGE_TMPLT = """# {{page.title}}
{% for tag in tags_and_pages %}
## {{tag.name}}
{% for page_info in tags_and_pages[tag] %}
* [{{ page_info.title }}]({{ page_info.rel_path }})
{% endfor %}
{% endfor %}
"""

_DFT_ON_PAGE_TMPLT = """{% set links = [] %}
{% for tag in tags %}
{{ links.append('[' + tag.name + '](' + tag_page_md_rel_path +
    '#' + tag.permalink + ')') or "" }}
{% endfor %}

{{ markdown }}
{% if tags %}
---
Tags: **{{ links | join('**, **')}}**
{% endif %}
"""


class _TagInfo:
    def __init__(self, name) -> None:
        self.name = name

        permalink_char_list = []
        for c in name:
            permalink_char_list.append(c if c != " " else "-")
            # BUG: repeated permalink not correctly handled
        self.permalink = "".join(permalink_char_list)

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: _TagInfo) -> bool:
        return self.name == other.name

    def __ne__(self, other: _TagInfo) -> bool:
        return not (self.name == other.name)


class _PageInfo:
    def __init__(self, page: pages.Page, tag_page_md_path: str) -> None:
        self.title: str = page.title
        self.abs_path = page.file.src_path
        self.rel_path = path.relpath(
            path=self.abs_path, start=path.dirname(tag_page_md_path)
        )


class MkDocsTags(plugins.BasePlugin):
    """An MkDocs plugin for tags support

    Not intended for direct import.

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
            config.config_options.Type(str, default="tags.md"),
        ),
    )

    def __init__(self) -> None:
        self._tags_and_pages: Dict[_TagInfo, List[_PageInfo]] = {}
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

    def on_nav(
        self, nav: nav.Navigation, config: config.Config, files: files.Files,
    ) -> nav.Navigation:
        """Reads tag and title info into `self.tags_and_pages`.

        See base class for argument and return value info.
        """
        config_copy = copy.copy(config)
        config_copy["plugins"] = plugins.PluginCollection()
        # Remove plugins in `config`. Otherwise,
        # `page_copy.read_source()` will call `on_page_read_source()`
        # for each plugin
        for page in nav.pages:
            page_copy = copy.copy(page)
            page_copy.read_source(config_copy)  # Read meta data
            if _TAGS_META_ENTRY not in page_copy.meta:
                continue
            tag_names = page_copy.meta[_TAGS_META_ENTRY]
            if not isinstance(tag_names, list):
                continue
            for tag_name in tag_names:
                if not isinstance(tag_name, str):
                    continue
                tag = _TagInfo(name=tag_name)
                if tag not in self._tags_and_pages:
                    self._tags_and_pages[tag] = []
                self._tags_and_pages[tag].append(
                    _PageInfo(
                        page=page_copy, tag_page_md_path=self._tag_page_md_path
                    )
                )
        # Sort the tags and the lists of pages under each of them
        for tag in self._tags_and_pages:
            self._tags_and_pages[tag].sort(key=operator.attrgetter("title"))
        self._tags_and_pages = {
            tag: self._tags_and_pages[tag]
            for tag in sorted(
                self._tags_and_pages, key=operator.attrgetter("name")
            )
        }
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
        if page.file.src_path == self._tag_page_md_path:
            jinja_tmplt = jinja2.Template(self._tag_page_tmplt)
            markdown = jinja_tmplt.render(
                tags_and_pages=self._tags_and_pages,
                markdown=markdown,
                page=page,
                config=config,
            )
        # Generate on-page tag lists
        if _TAGS_META_ENTRY not in page.meta:
            return markdown
        tag_names = page.meta[_TAGS_META_ENTRY]
        tags: List[_TagInfo] = []
        if not isinstance(tag_names, list):
            return markdown
        for tag_name in tag_names:
            if not isinstance(tag_name, str):
                continue
            tag = _TagInfo(name=tag_name)
            tags.append(tag)
        jinja_tmplt = jinja2.Template(self._on_page_tmplt)
        tag_page_md_rel_path = path.relpath(
            path=self._tag_page_md_path, start=path.dirname(page.file.src_path)
        )
        markdown = jinja_tmplt.render(
            tags=tags,
            markdown=markdown,
            page=page,
            config=config,
            tag_page_md_rel_path=tag_page_md_rel_path,
        )
        return markdown

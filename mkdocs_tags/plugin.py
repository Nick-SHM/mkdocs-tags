# Copyright 2020 Nick Shu <nick.shm.shu.git@outlook.com>
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
"""A tags plugin for MkDocs

This plugin reads tags info from the metadata section from each
page, generate a list of tags on each page, and generate a tags page
with a list of all tags and the pages under each of them.

Not intended for direct usage.
"""

import copy
import jinja2
from mkdocs import config
from mkdocs.structure import files
from mkdocs.structure import nav
from mkdocs.structure import pages
from mkdocs import plugins
from os import path
from typing import Dict

_TAGS_META_ENTRY = 'tags'
_ON_PAGE_TMPLT_CFG_ENTRY = 'on_page_tmplt'
_ON_PAGE_TMPLT_PATH_CFG_ENTRY = 'on_page_tmplt_path'
_TAGS_PAGE_TMPLT_CFG_ENTRY = 'tags_page_tmplt'
_TAGS_PAGE_TMPLT_PATH_CFG_ENTRY = 'tags_page_tmplt_path'
_TAGS_PAGE_MD_PATH_CFG_ENTRY = 'tags_page_md_path'

_DFT_TAGS_PAGE_TMPLT = """# {{page.title}}
{% for tag in tags_and_pages %}
## {{tag}}
{% for page_under_tag in tags_and_pages[tag] %}
* [{{page_under_tag["title"]}}]({{page_under_tag["path"]}})
{% endfor %}
{% endfor %}
"""

_DFT_ON_PAGE_TMPLT = """{{markdown}}
{% if empty %}

---

Tags: **{{ tags | join("**, **") }}**
{% endif %}
"""


class MkDocsTags(plugins.BasePlugin):
    """A tags plugin for MkDocs

    Not intended for direct usage.

    Attributes:
        config_scheme: see base class
    """

    config_scheme = (
        (
            _TAGS_PAGE_TMPLT_CFG_ENTRY,
            config.config_options.Type(str, default=_DFT_TAGS_PAGE_TMPLT),
        ),
        (
            _TAGS_PAGE_TMPLT_PATH_CFG_ENTRY,
            config.config_options.Type(str, default=''),
        ),
        (
            _ON_PAGE_TMPLT_CFG_ENTRY,
            config.config_options.Type(str, default=_DFT_ON_PAGE_TMPLT),
        ),
        (
            _ON_PAGE_TMPLT_PATH_CFG_ENTRY,
            config.config_options.Type(str, default=''),
        ),
        (
            _TAGS_PAGE_MD_PATH_CFG_ENTRY,
            config.config_options.Type(str, default='tags.md'),
        ),
    )

    def __init__(self):
        self._tags_and_pages: Dict[str, Dict[str, str]] = {}
        self._tags_page_md_path = ''
        self._tags_page_tmplt = ''
        self._on_page_tmplt = ''

    def on_config(self, config: config.Config) -> config.Config:
        """Determines the templates from the config.

        See base class for arguments and return value info.
        """
        # Read the path of tags page markdown file
        self._tags_page_md_path = self.config[_TAGS_PAGE_MD_PATH_CFG_ENTRY]
        # Read the template of the tags page
        tags_page_tmplt_path = self.config[_TAGS_PAGE_TMPLT_PATH_CFG_ENTRY]
        docs_dir = config['docs_dir']
        if tags_page_tmplt_path == '':
            self._tags_page_tmplt = self.config[_TAGS_PAGE_TMPLT_CFG_ENTRY]
        else:
            with open(path.join(docs_dir, tags_page_tmplt_path)) as file:
                self._tags_page_tmplt = file.read()
        # Read the template of on-page tags lists
        on_page_tmplt_path = self.config[_ON_PAGE_TMPLT_PATH_CFG_ENTRY]
        if on_page_tmplt_path == '':
            self._on_page_tmplt = self.config[_ON_PAGE_TMPLT_CFG_ENTRY]
        else:
            with open(path.join(docs_dir, on_page_tmplt_path)) as file:
                self._on_page_tmplt = file.read()
        return config

    def on_nav(
        self,
        nav: nav.Navigation,
        config: config.Config,
        files: files.Files,
    ) -> nav.Navigation:
        """Reads tags and title info into `self.tags_and_pages`.

        See base class for arguments and return value info.
        """
        config_copy = copy.copy(config)
        config_copy['plugins'] = plugins.PluginCollection()
        # Remove plugins in `config`. Otherwise,
        # `page_copy.read_source()` will call `on_page_read_source()`
        # for each plugin
        for page in nav.pages:
            page_copy = copy.copy(page)
            page_copy.read_source(config_copy)  # Read meta data
            if _TAGS_META_ENTRY not in page_copy.meta:
                continue
            tags = page_copy.meta[_TAGS_META_ENTRY]
            if isinstance(tags, list):
                for tag in tags:
                    if isinstance(tag, str):
                        if tag not in self._tags_and_pages:
                            self._tags_and_pages[tag] = []
                        page_path = path.relpath(
                            page_copy.file.src_path,
                            path.dirname(self._tags_page_md_path))
                        self._tags_and_pages[tag].append({
                            'title': page_copy.title,
                            'path': page_path
                        })
        return nav

    def on_page_markdown(
        self,
        markdown: str,
        page: pages.Page,
        config: config.Config,
        files: files.Files,
    ) -> str:
        """Generates on-page tags lists and the tags page.

        See base class for arguments and return value info.
        """
        # Generate the tags page
        if page.file.src_path == self._tags_page_md_path:
            jinja_tmplt = jinja2.Template(self._tags_page_tmplt)
            markdown = jinja_tmplt.render(
                tags_and_pages=self._tags_and_pages,
                markdown=markdown,
                page=page,
                config=config,
            )
        # Generate on-page tags lists
        if _TAGS_META_ENTRY not in page.meta:
            return markdown
        tags = page.meta[_TAGS_META_ENTRY]
        if isinstance(tags, list):
            str_tags = []  # tags that are `str`
            for tag in tags:
                if isinstance(tag, str):
                    str_tags.append(tag)
            jinja_tmplt = jinja2.Template(self._on_page_tmplt)
            markdown = jinja_tmplt.render(
                tags=str_tags,
                markdown=markdown,
                empty=bool(str_tags),
                page=page,
                config=config,
            )
        return markdown

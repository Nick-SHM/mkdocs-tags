import copy
from jinja2 import Template
from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin
from mkdocs.plugins import PluginCollection
from os.path import relpath, dirname


class MkDocsTags(BasePlugin):
    """
    An MkDocs plugin to generate tags in the YAML metadata on each page and on
    a tags page.
    """

    dft_tags_page_tmplt = (
        '# Tags\n'
        '{% for tag in tags_and_pages %}\n'
        '## {{tag}}\n'
        '{% for page in tags_and_pages[tag] %}\n'
        '* [{{page["title"]}}]({{page["path"]}})\n'
        '{% endfor %}\n'
        '{% endfor %}\n'
    )

    dft_on_page_tmplt = (
        '{{markdown}}\n'
        '{% if empty %}\n'
        '\n'
        '---\n'
        '\n'
        'Tags: **{{ tags | join("**, **") }}**\n'
        '{% endif %}\n'
    )

    tags_meta_entry = 'tags'

    tags_page_tmplt_cfg = 'tags-page-tmplt'
    tags_page_tmplt_path_cfg = 'tags-page-tmplt-path'
    on_page_tmplt_cfg = 'on-page-tmplt'
    on_page_tmplt_path_cfg = 'on-page-tmplt-path'
    tags_page_md_path_cfg = 'tags-page-md-path'

    config_scheme = (
        (
            tags_page_tmplt_cfg,
            config_options.Type(str, default=dft_tags_page_tmplt)
        ),
        (
            tags_page_tmplt_path_cfg,
            config_options.Type(str, default='')
        ),
        (
            on_page_tmplt_cfg,
            config_options.Type(str, default=dft_on_page_tmplt)
        ),
        (
            on_page_tmplt_path_cfg,
            config_options.Type(str, default='')
        ),
        (
            tags_page_md_path_cfg,
            config_options.Type(str, default='tags.md')
        )
    )

    def __init__(self):
        self.tags_and_pages = {}
        self.tags_page_md_path = ''
        self.tags_page_tmplt = ''
        self.on_page_tmplt = ''

    def on_config(self, config):
        """ Determines the templates from the config"""
        # Read the path of tags page markdown file
        self.tags_page_md_path = self.config[MkDocsTags.tags_page_md_path_cfg]
        # Read the template of the tags page
        tags_page_tmplt_path = self.config[MkDocsTags.tags_page_tmplt_path_cfg]
        docs_dir = config['docs_dir']
        if tags_page_tmplt_path == '':
            self.tags_page_tmplt = self.config[MkDocsTags.tags_page_tmplt_cfg]
        else:
            with open(docs_dir + '/' + tags_page_tmplt_path) as file:
                self.tags_page_tmplt = file.read()
        # Read the template of on-page tags lists
        on_page_tmplt_path = self.config[MkDocsTags.on_page_tmplt_path_cfg]
        if on_page_tmplt_path == '':
            self.on_page_tmplt = self.config[MkDocsTags.on_page_tmplt_cfg]
        else:
            with open(docs_dir + '/' + on_page_tmplt_path) as file:
                self.on_page_tmplt = file.read()
        return config

    def on_nav(self, nav, config, files):
        """ Read tags and title info into `self.tags_and_pages` """
        config_copy = copy.copy(config)
        config_copy['plugins'] = PluginCollection()
        # Remove plugins in config. Otherwise, `page_copy.read_source()` will
        # call `on_page_read_source()` for each plugin
        for page in nav.pages:
            page_copy = copy.copy(page)
            page_copy.read_source(config_copy)  # Read meta data
            if MkDocsTags.tags_meta_entry not in page_copy.meta:
                continue
            tags = page_copy.meta[MkDocsTags.tags_meta_entry]
            if isinstance(tags, list):
                for tag in tags:
                    if isinstance(tag, str):
                        if tag not in self.tags_and_pages:
                            self.tags_and_pages[tag] = []
                        path = relpath(page_copy.file.src_path, dirname(
                            self.tags_page_md_path))
                        self.tags_and_pages[tag].append({
                            'title': page_copy.title, 'path': path})
        return nav

    def on_page_markdown(self, markdown, page, config, files):
        """ Generate on-page tags lists and the tags page """
        # Generate the tags page
        if page.file.src_path == self.tags_page_md_path:
            jinja_tmplt = Template(self.tags_page_tmplt)
            markdown = jinja_tmplt.render(tags_and_pages=self.tags_and_pages)
        # Generate on-page tags lists
        if MkDocsTags.tags_meta_entry not in page.meta:
            return markdown
        tags = page.meta[MkDocsTags.tags_meta_entry]
        if isinstance(tags, list):
            str_tags = []
            for tag in tags:
                if isinstance(tag, str):
                    str_tags.append(tag)
            jinja_tmplt = Template(self.on_page_tmplt)
            markdown = jinja_tmplt.render(
                tags=str_tags, markdown=markdown, empty=bool(str_tags))
        return markdown

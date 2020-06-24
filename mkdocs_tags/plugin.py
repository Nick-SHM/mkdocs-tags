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
        "# Tags\n"
        "{% for tag in tags_and_pages %}\n"
        "## {{tag}}\n"
        "{% for page in tags_and_pages[tag] %}\n"
        "* [{{page['title']}}]({{page['src']}})\n"
        "{% endfor %}\n"
        "{% endfor %}\n"
    )

    dft_on_page_tmplt = (
        "{{markdown}}\n"
        "{% if empty %}\n"
        "\n"
        "---\n"
        "\n"
        "Tags: **{{ tags | join('**, **') }}**\n"
        "{% endif %}\n"
    )

    config_scheme = (
        (
            'tags-page-tmplt',
            config_options.Type(str, default=dft_tags_page_tmplt)
        ),
        (
            'tags-page-tmplt-path',
            config_options.Type(str, default='')
        ),
        (
            'on-page-tmplt',
            config_options.Type(str, default=dft_on_page_tmplt)
        ),
        (
            'on-page-tmplt-path',
            config_options.Type(str, default='')
        ),
        (
            'tags-page-md-path',
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
        # Tags page markdown path
        self.tags_page_md_path = self.config['tags-page-md-path']
        # Tags page template
        if self.config['tags-page-tmplt-path'] == '':
            self.tags_page_tmplt = self.config['tags-page-tmplt']
        else:
            with open(config['docs_dir'] + '/' +
                      self.config['tags-page-tmplt-path']) as file:
                self.tags_page_tmplt = file.read()
        # On-page tags template
        if self.config['on-page-tmplt-path'] == '':
            self.on_page_tmplt = self.config['on-page-tmplt']
        else:
            with open(config['docs_dir'] + '/' +
                      self.config['on-page-tmplt-path']) as file:
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
            if 'tags' in page_copy.meta and isinstance(
                    page_copy.meta['tags'], list):
                for tag in page_copy.meta['tags']:
                    if tag not in self.tags_and_pages:
                        self.tags_and_pages[tag] = []
                    path = relpath(
                        page_copy.file.src_path,
                        dirname(self.tags_page_md_path))
                    self.tags_and_pages[tag].append({
                        'title': page_copy.title,
                        'src': path
                    })

    def on_page_markdown(self, markdown, page, config, files):
        """ Generate on-page tags and the tags page"""
        if page.file.src_path == self.tags_page_md_path:
            jinja_tmplt = Template(self.tags_page_tmplt)
            markdown = jinja_tmplt.render(tags_and_pages=self.tags_and_pages)
        if 'tags' in page.meta and isinstance(page.meta['tags'], list):
            jinja_tmplt = Template(self.on_page_tmplt)
            markdown = jinja_tmplt.render(
                tags=page.meta['tags'],
                markdown=markdown,
                empty=bool(page.meta['tags']),  # whether the list is empty
            )
        return markdown

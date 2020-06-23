import copy
from jinja2 import Template
from mkdocs.plugins import BasePlugin
from mkdocs.plugins import PluginCollection


class MkDocsTags(BasePlugin):
    """
    An MkDocs plugin to generate tags in the YAML metadata on each page and on
    a tags page.
    """

    def __init__(self):
        self.tags_and_pages = {}
        # TODO: Customizable tags page path
        self.tags_page_src_path = 'tags.md'

    def on_nav(self, nav, config, files):
        """ Read tags and title info into `self.tags_and_pages` """
        config_copy = copy.deepcopy(config)
        config_copy['plugins'] = PluginCollection()
        # Remove plugins in config. Otherwise, `page_copy.read_source()` will
        # call `on_page_read_source()` for each plugin
        for page in nav.pages:
            page_copy = copy.deepcopy(page)
            page_copy.read_source(config_copy)
            if 'tags' not in page_copy.meta:
                pass
            elif not isinstance(page_copy.meta['tags'], list):
                pass
            else:
                for tag in page_copy.meta['tags']:
                    if isinstance(tag, str):
                        if tag not in self.tags_and_pages:
                            self.tags_and_pages[tag] = []
                        self.tags_and_pages[tag].append({
                            'title': page_copy.title,
                            'src': page.file.src_path
                        })

    def on_page_markdown(self, markdown, page, config, files):
        """ Generate on-page tags and the tags page"""
        if page.file.src_path == self.tags_page_src_path:
            jinja_tmplt_str = """# Tags
{% for tag in tags_and_pages %}
## {{tag}}
{% for page in tags_and_pages[tag] %}
* [{{page['title']}}]({{page['src']}})
{% endfor %}
{% endfor %}
"""
            jinja_tmplt = Template(jinja_tmplt_str)
            return jinja_tmplt.render(tags_and_pages=self.tags_and_pages)
        else:
            jinja_tmplt_str = """{{markdown}}
{% if empty %}

---

Tags: **{{ tags | join('**, **') }}**

{% endif %}
"""
            if 'tags' in page.meta and isinstance(page.meta['tags'], list):
                jinja_tmplt = Template(jinja_tmplt_str)
                return jinja_tmplt.render(
                    tags=page.meta['tags'],
                    markdown=markdown,
                    empty=bool(page.meta['tags']),  # whether the list is empty
                )
            else:
                return markdown

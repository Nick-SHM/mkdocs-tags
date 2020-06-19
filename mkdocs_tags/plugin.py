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
        self.tags_page_src_path = "tags.md"

    def on_nav(self, nav, config, files):
        """ Read tags and title info into `self.tags_and_pages` """
        config_copy = copy.deepcopy(config)
        config_copy['plugins'] = PluginCollection()
        # Remove plugins in config. Otherwise, `page_copy.read_source()` will
        # call `on_page_read_source()` for each plugin
        for page in nav.pages:
            page_copy = copy.deepcopy(page)
            page_copy.read_source(config_copy)
            if "tags" not in page_copy.meta:
                pass
            elif not isinstance(page_copy.meta["tags"], list):
                pass
            else:
                for tag in page_copy.meta["tags"]:
                    if isinstance(tag, str):
                        if tag not in self.tags_and_pages:
                            self.tags_and_pages[tag] = []
                        self.tags_and_pages[tag].append(
                            {"title": page_copy.title,
                             "src": page.file.src_path})

    def on_page_markdown(self, markdown, page, config, files):
        """ Generate on-page tags and the tags page"""
        if page.file.src_path == self.tags_page_src_path:
            # TODO: Customizable tags page template
            jinja_template_str = """# Tags
{% for tag in tags_and_pages %}
## {{tag}}
{% for page in tags_and_pages[tag] %}
* [{{page['title']}}]({{page['src']}})
{% endfor %}
{% endfor %}
"""
            jinja_template = Template(jinja_template_str)
            return jinja_template.render(tags_and_pages=self.tags_and_pages)
        else:
            # TODO: Customizable on-page tags
            tag_str_list = ['\n---\n\nTags:']
            if "tags" not in page.meta:
                pass
            elif not isinstance(page.meta["tags"], list):
                pass
            else:
                for tag in page.meta["tags"]:
                    if isinstance(tag, str):
                        tag_str_list.append(' **')
                        tag_str_list.append(tag)
                        tag_str_list.append('**')
                        tag_str_list.append(',')
                tag_str_list[-1] = ''
            return markdown + ''.join(tag_str_list)

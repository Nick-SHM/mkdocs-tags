# MkDocs Tags Plugin

A tags plugin for [MkDocs](https://www.mkdocs.org).

**Features might not be backward compatible until v1.0.**

## Installation

```bash
pip install git+https://github.com/Nick-SHM/mkdocs-tags.git
```

Installation through [PyPI](https://pypi.org) will be available in the future.

## Quick Start

Create an MkDocs site:

```bash
mkdocs new demo
```

Add `tags` to the `plugins` entry of `mkdocs.yml`.

```yaml
site_name: My Docs

plugins:
    - search
    - tags
```

_Note that if you have previously omitted this entry, you'll likely want to enable the plugin `search` as well. MkDocs enables it by default, but now you have to enable it explicitly._

Add tags to a page as a list in the `tags` entry of the [metadata section](https://www.mkdocs.org/user-guide/writing-your-docs/#meta-data). For example, change `index.md` to:

```
---
tags:
    - tag1
    - tag2
---

# Index
```

Then, by default, a list of tags will be generated on the bottom of the page, if the page contains at least one tag.

![On-page tag list](img/demo-index.png)

Create `tags.md` in `docs/`. This file will contain a list of all tags and the pages under each of them.

![Tags page](img/demo-tags-page.png)

You can add this page to an arbitrary place under the `nav` entry in `mkdocs.yml`. This page can also have tags, but by default, all the content in the file other than the metadata and the title will be ignored.

## Detailed Guide

### Tags Page

A page with a list of all tags and the pages under each of them will be rendered using [Jinja](https://jinja.palletsprojects.com). Customization options include:

Options should be put in `mkdocs.yml` under the plugin entry. For example:

```yaml
plugins:
    - search
    - tags:
          tags_page_md_path: path/to/tags/page.md
```

-   `tags_page_md_path`: the path, relative to `docs/`, to the markdown file which will be rendered as the tags page. The default value is `tags.md`.
-   `tags_page_tmplt_path`: the path, **relative to `docs/`**, to the Jinja template file.
-   `tags_page_tmplt`: the template as a string.

If both `tags_page_tmplt_path` and `tags_page_tmplt` are set, `tags_page_tmplt` will be ignored. If neither of them is set, the default template is:

```jinja
# {{page.title}}
{% for tag in tags_and_pages %}
## {{tag}}
{% for page_under_tag in tags_and_pages[tag] %}
* [{{page_under_tag["title"]}}]({{page_under_tag["path"]}})
{% endfor %}
{% endfor %}
```

All the variables available for the template include:

-   `tags_and_pages`: a `dict` containing tags and pages info, see the default template about its usage. **This is subject to change until the release of v1.0.**
-   `markdown`: the markdown source of the page, in a `str`.
-   `page`: the `mkdocs.structure.pages.Page` object of the current page. For more info, see [MkDocs documentation](https://www.mkdocs.org/user-guide/custom-themes/#page) and [MkDocs source code](https://github.com/mkdocs/mkdocs/blob/master/mkdocs/structure/pages.py).
-   `config`: the global `mkdocs.config.base.Config` object of the site. For more info, see [MkDocs documentation](https://www.mkdocs.org/user-guide/custom-themes/#config) and [MkDocs source code](https://github.com/mkdocs/mkdocs/blob/master/mkdocs/config/base.py).

### On-page Tags List

A list of tags will be rendered on the bottom of the page using [Jinja](https://jinja.palletsprojects.com). Customization options include:

-   `on_page_tmplt_path`: the path, **relative to `docs/`**, to the Jinja template file.
-   `on_page_tmplt`: the template as a string.

If both options are set, `on_page_tmplt` will be ignored. If neither of them is set, the default template is:

```jinja
{{markdown}}
{% if empty %}

---

Tags: **{{ tags | join("**, **") }}**
{% endif %}
```

All the variables available for the template include:

-   `tags`: all the tags of this page, in a `list`.
-   `markdown`: the markdown source of the page, in a `str`.
-   `empty`: whether the page contains at least one tag.
-   `page`: the `mkdocs.structure.pages.Page` object of the current page. For more info, see [MkDocs documentation](https://www.mkdocs.org/user-guide/custom-themes/#page) and [MkDocs source code](https://github.com/mkdocs/mkdocs/blob/master/mkdocs/structure/pages.py). Not all the attributes of `page` is available when the plugin renders the page.
-   `config`: the global `mkdocs.config.base.Config` object of the site. For more info, see [MkDocs documentation](https://www.mkdocs.org/user-guide/custom-themes/#config) and [MkDocs source code](https://github.com/mkdocs/mkdocs/blob/master/mkdocs/config/base.py).

## License

This project is under [Apache License 2.0](LICENSE).

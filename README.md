# MkDocs Tags Plugin

A tags plugin for [MkDocs](https://www.mkdocs.org).

## Getting Started

### Installation

With `pip`:

```bash
pip install git+https://github.com/Nick-SHM/mkdocs-tags.git
```

### Setting up

First, add `tags` to the `plugins` entry of `mkdocs.yml`.

Note that if you have previously omitted this entry, you'll likely want to enable the plugin `search` as well. MkDocs enables it by default, but now you have to enable it explicitly.

```yaml
plugins:
    - search
    - tags
```

Second, add a blank `tags.md` file in `docs/` and add it to the `nav` entry in `mkdocs.yml`. This file will be generated as a list of all tags with the pages under them. This page can also have tags, but the all the content in the file other than metadata and the title will be ignored. Customization options will be available in the future.

### Add Tags to Pages

Add tags as a list to the `tags` entry in the [metadata section](https://www.mkdocs.org/user-guide/writing-your-docs/#meta-data) of the page.

```markdown
---
tags:
    - tag1
    - tag2
---

# Title

content
```

Tags will be rendered on the bottom of the page. Customization options will be available in the future.

## License

This project is under [Apache License 2.0](LICENSE).

# Change Log

## [0.4] -

### Added

-   Links to the section of the tags page in the on-page tag lists

### Changed

-   **Breaking API change**: change config entry `tags_page_tmplt` to `tag_page_tmplt`
-   **Breaking API change**: change config entry `tags_page_tmplt_path` to `tag_page_tmplt_path`
-   **Breaking API change**: change config entry `tags_page_md_path` to `tag_page_md_path`
-   **Breaking API change**: add new type `_TagInfo` to replace the original `str` approach
-   **Breaking API change**: add new type `_PageInfo` to replace the original `dict` approach
-   Tags and pages are now sorted on the tags page
-   Temporarily removed `README.md`
-   Add a link to changelog in `README.md`
-   Fix typos in comments and `README.md`

## [0.3] - 2020-06-30

### Added

-   Add CHANGELOG
-   Add CONTRIBUTING
-   Add CODE_OF_CONDUCT
-   Add EditorConfig

### Changed

-   Comply with [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
-   Improve README
    -   Adjust structure
    -   Add reminder for no backward compatibility before v1.0
    -   Fix typos
-   Add GitHub gitignore for Python

## [0.2] - 2020-06-26

### Added

-   Customizable tags page template
-   Customizable on-page tags list template
-   Customizable tags page markdown file path

### Fixed

-   Bug that links on the tags page are not relative

### Changed:

-   Change the entry in `tags_and_pages` for the path of a page from `src` to `path`
-   Improve README
    -   Adjust structure
    -   Customization guide
    -   Fix typos
-   Comply to PEP 8

## [0.1] - 2020-06-19

### Added:

-   Generate the tags page
-   Generate on-page tags lists

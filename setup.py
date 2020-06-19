import os
from setuptools import setup, find_packages


def get_readme():
    """ Read `README.md` and return it as a string """
    return open(os.path.join(os.path.dirname(__file__), 'README.md')).read()


setup(
    name="mkdocs-tags",
    version="0.1",
    description="Tags plugin for MkDocs",
    long_description=get_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Nick-SHM/mkdocs-tags",
    author="Nick Shu",
    author_email="nick.shm.shu.git+noreply@outlook.com",
    license='Apache',
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Intended Audience :: Developers",
        "Topic :: Documentation",
        "Topic :: Software Development :: Documentation"
    ],
    keywords='mkdocs tag',
    packages=find_packages(),
    install_requires=[
        'mkdocs'
    ],
    python_requires='>=3.6',
    entry_points={
        'mkdocs.plugins': [
            'tags = mkdocs_tags.plugin:MkDocsTags'
        ]
    }
)

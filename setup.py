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

from os import path
import setuptools

with open(path.join(path.dirname(__file__), "README.md")) as readme:
    setuptools.setup(
        name="mkdocs-tags",
        version="1.0",
        description="An MkDocs plugin for tags support",
        long_description=readme.read(),
        long_description_content_type="text/markdown",
        url="https://github.com/Nick-SHM/mkdocs-tags",
        author="Nick Shu",
        author_email="nick.shm.shu.git+noreply@outlook.com",
        license="Apache",
        classifiers=[
            "License :: OSI Approved :: Apache Software License",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3 :: Only",
            "Intended Audience :: Developers",
            "Topic :: Documentation",
            "Topic :: Software Development :: Documentation",
        ],
        keywords="mkdocs tag",
        packages=setuptools.find_packages(),
        install_requires=["mkdocs"],
        python_requires=">=3.6",
        entry_points={"mkdocs.plugins": ["tags = mkdocs_tags:MkDocsTags"]},
    )

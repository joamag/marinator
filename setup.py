#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import setuptools

setuptools.setup(
    name = "marinator",
    version = "0.2.2",
    author = "João Magalhães",
    author_email = "joamag@gmail.com",
    description = "The power of a Marina for everyone",
    license = "Apache License, Version 2.0",
    keywords = "ripe api",
    url = "http://www.joao.me",
    zip_safe = False,
    packages = [
        "marinator"
    ],
    package_dir = {
        "" : os.path.normpath("src")
    },
    install_requires = [
        "appier",
        "appier_console",
        "ripe_api",
        "PyPDF2"
    ],
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.0",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7"
    ],
    long_description = open(os.path.join(os.path.dirname(__file__), "README.md"), "r").read(),
    long_description_content_type = "text/markdown"
)

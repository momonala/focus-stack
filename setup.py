# -*- coding: utf-8 -*-
import setuptools
from setuptools import setup

from focus_stack import __version__

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="focus-stack",
    version=__version__,
    author="Mohit Nalavadi",
    author_email="mnalavadi@gmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/momonala/focus-stack",
    description="Tool to focus stack images.",
    packages=setuptools.find_packages(),
    package_dir={"focus_stack": "focus_stack"},
    entry_points={"console_scripts": ["focusstack = focus_stack.run:main"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)

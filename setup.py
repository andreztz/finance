from setuptools import setup, find_packages
from pathlib import Path

from typing import Any


DESCRIPTION = """Projeto desenvolvido durante o curso CS50 da
    Fundação Estudar"""


def read(filename: Path) -> Any:
    match filename.suffix:
        case ".txt":
            return [line.strip() for line in open(filename).readlines()]
        case ".md":
            return filename.read_text()


setup(
    name="finance",
    version="0.1.0",
    author="Andre P. Santos",
    author_email="andreztz@gmail.com",
    license="MIT",
    long_description=read(Path("readme.md")),
    long_description_content_type="text/markdown",
    description=DESCRIPTION,
    install_requires=read(Path("requirements.txt")),
    extras_requires={"dev": read(Path("requirements-dev.txt"))},
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.10",
)

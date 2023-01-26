from typing import List

import setuptools


def read_multiline_as_list(file_path: str) -> List[str]:
    with open(file_path) as req_file:
        contents = req_file.read().split("\n")
        if contents[-1] == "":
            contents.pop()
        return contents


with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

requirements = read_multiline_as_list("requirements.txt")
requirements_first = read_multiline_as_list("requirements-first.txt")

setuptools.setup(
    name="oauth-middleware",
    version="0.1.0",
    author="Teialabs",
    author_email="contato@teialabs.com",
    description="OAuth middleware compatible with FastAPI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TeiaLabs/OAuth-FastAPI",
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    keywords='fastapi middleware oauth cognito ad active directory',
    python_requires=">=3.9",
    install_requires=requirements,
    extra_requires={
        "first": requirements_first
    }
)

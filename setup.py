import epsilon
import setuptools

with open("epsilon/version.py") as f:
    exec(f.read())

setuptools.setup(
    name = "epsilon",
    version = VERSION,
    python_requires = ">=3.6",

    author = "Michael Paddon",
    author_email = "michael@paddon.org",
    description = "A lexical scanner generator.",
    url = "https://github.com/MichaelPaddon/epsilon",
    license = "GPLv3",
    keywords = "lexer scanner",

    packages = setuptools.find_packages(),
    include_package_data = True,
    entry_points = {
        "console_scripts": ["epsilon = epsilon.cli:main"]
    },
)

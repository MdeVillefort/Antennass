import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# Version: major.minor.patch
VERSION = "1.0.1"

REQUIREMENTS = (HERE / "requirements.txt").read_text()
REQUIREMENTS = REQUIREMENTS.split('\n')

# This call to setup() does all the work
setup(
    name = "Antennass",
    version = VERSION,
    description = "A class project that plots far field antenna array patterns",
    long_description = README,
    long_description_content_type = "text/markdown",
    url = "https://github.com/MdeVillefort/Antennass",
    author = "Monsieur de Villefort",
    author_email = "ethanmross92@gmail.com",
    classifiers = [
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8"
    ],
    packages = ["Antennass"],
    install_requires = REQUIREMENTS,
    entry_points = {
        "console_scripts" : [
            "antennass-cli=Antennass.antennass_cli:main",
            "antennass-gui=Antennass.antennass_gui:main",
        ]
    },
)

from __future__ import print_function

import os
import sys

from setuptools import find_packages, setup

# the name of the project
name = "pyalect"

# basic paths used to gather files
here = os.path.abspath(os.path.dirname(__file__))
root = os.path.join(here, name)


# -----------------------------------------------------------------------------
# Package Definition
# -----------------------------------------------------------------------------


package = {
    "name": name,
    "python_requires": ">=3.6,<4.0",
    "packages": find_packages(exclude=["tests*"]),
    "description": "",
    "author": "Ryan Morshead",
    "author_email": "ryan.morshead@gmail.com",
    "url": "https://github.com/rmorshea/pyalect",
    "license": "MIT",
    "platforms": "Linux, Mac OS X, Windows",
    "keywords": [],
    "include_package_data": True,
}


# -----------------------------------------------------------------------------
# Requirements
# -----------------------------------------------------------------------------


requirements = []
with open(os.path.join(here, "requirements", "prod.txt"), "r") as f:
    for line in map(str.strip, f):
        if not line.startswith("#"):
            requirements.append(line)
package["install_requires"] = requirements

_current_extra_section = None
extra_requirements = {"all": []}
extra_requirements_path = os.path.join(here, "requirements", "extras.txt")
with open(extra_requirements_path, "r") as f:
    for line in map(str.strip, f):
        if line.startswith("#") and line[1:].strip().startswith("extra="):
            _current_extra_section = line.split("=", 1)[1]
            if _current_extra_section == "all":
                raise ValueError("%r uses the reserved extra name 'all'")
            extra_requirements[_current_extra_section] = []
        elif _current_extra_section is not None:
            extra_requirements[_current_extra_section].append(line)
            extra_requirements["all"].append(line)
        elif line:
            msg = "No '# extra=<name>' header before requirements in %r"
            raise ValueError(msg % extra_requirements_path)
package["extras_require"] = extra_requirements

# -----------------------------------------------------------------------------
# Library Version
# -----------------------------------------------------------------------------


with open(os.path.join(root, "__init__.py")) as f:
    for line in f.read().split("\n"):
        if line.startswith("__version__ = "):
            version = eval(line.split("=", 1)[1])
            break
    else:
        print("No version found in __init__.py")
        sys.exit(1)
package["version"] = version


# -----------------------------------------------------------------------------
# Library Description
# -----------------------------------------------------------------------------


with open(os.path.join(here, "README.md")) as f:
    long_description = f.read()

package["long_description"] = long_description
package["long_description_content_type"] = "text/markdown"


# -----------------------------------------------------------------------------
# Install It
# -----------------------------------------------------------------------------


if __name__ == "__main__":
    setup(**package)

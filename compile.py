# This file is part of PyImgur.

# PyImgur is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# PyImgur is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with PyImgur.  If not, see <http://www.gnu.org/licenses/>.

"""Compile stage. Run after cursor change to ensure quality."""

import subprocess

import os

os.environ["FAST_TESTS"] = "TRUE"

# Tests are placed first to allow for fast failing. In this case subsequent things are
# not run. This allows for a shorter turn around with Cursor as it more quickly discovers
# errors.
subprocess.run(
    r"pytest tests",
    shell=True,
    check=True,
)

# Next everything is linted
print("Linting package...")
subprocess.run(r"pylint pyimgur *.py", shell=True, check=True)

print("Linting tests...")
subprocess.run(
    r"pylint tests --disable missing-function-docstring,missing-module-docstring,"
    "protected-access,missing-class-docstring",
    shell=True,
    check=True,
)

# Everything is good. Cleanup. This should never fail...
print("Formatting code and documentation...")
subprocess.run(r"black *.py pyimgur tests", shell=True, check=True)
subprocess.run(r"prettier --write README.md", shell=True, check=True)

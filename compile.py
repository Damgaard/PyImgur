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
subprocess.run(r"pylint pyimgur", shell=True, check=True)

print("Linting tests...")
subprocess.run(
    r"pylint tests --disable missing-function-docstring,missing-module-docstring,protected-access,missing-class-docstring",
    shell=True,
    check=True,
)

# Everything is good. Cleanup. This should never fail...
print("Formatting code and documentation...")
subprocess.run(r"black *.py pyimgur tests", shell=True, check=True)
subprocess.run(r"prettier --write README.md", shell=True, check=True)

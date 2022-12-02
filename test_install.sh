#!/bin/bash

# Build the distribution
original_directory=$(pwd)
distfile="${original_directory}/dist/$(poetry build -f sdist | tail -1 | awk -F' ' '{print $NF}')"

# Create a new tempfile for the test
tempdir=$(mktemp -d)
echo "new temporary directory: ${tempdir}"

# Copy the test files
echo "copying the test files"
cp -r -v "${original_directory}/tests" "${tempdir}/."

# Change to the new directory
echo "change to the new directory"
cd "$tempdir" || exit

# Create a new virtualenv and install the distribution
echo "creating new virtualenv"
virtualenv venv

echo "activating new venv"
# shellcheck source=/dev/null
source venv/bin/activate

echo "installing distribution file ${distfile}"
pip install "${distfile}"
pip install pytest

echo "Installed version of AutoRA: $(python -c 'import autora; print(autora.__version__)')"

echo "running unit tests:"
pytest

echo "Run and test using:"
echo "cd \"${tempdir}\""
echo "source ${tempdir}/venv/bin/activate"
echo "python -c 'import autora; print(autora.__version__)'"
echo "pytest"
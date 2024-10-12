Here’s a structured and concise guide for **pip**, mimicking the style used for Helm:

# pip

pip is the package installer for Python. You can use it to install packages from the Python Package Index (PyPI) and other sources.

#platform/multiple #target/Python #cat/PackageManagement

% pip, python, package management, installation

## pip - Install Package from PyPI

Install a package from the Python Package Index (PyPI).

```
pip install <package>
```

Example:

```
pip install requests
```

## pip - Install Package from a Local Wheel File

Install a Python package from a local wheel (.whl) file.

```
pip install <path_to_wheel_file>
```

Example:

```
pip install requests-2.22.0-py2.py3-none-any.whl
```

## pip - Install Package from a Git Repository

Install a package directly from a Git repository.

```
pip install git+<git_url>
```

Example:

```
pip install git+https://github.com/psf/requests.git
```

## pip - Install Package from a Local Directory

Install a package from a local directory that contains the package source code.

```
pip install <directory_path>
```

Example:

```
pip install /home/user/src/requests
```

## pip - Search for Packages

Search for packages in PyPI by a specific term.

```
pip search <term>
```

Example:

```
pip search requests
```

## pip - Show Package Details

Show detailed information about a specific installed package.

```
pip show <package>
```

Example:

```
pip show requests
```

## pip - Download a Package

Download a package and its dependencies without installing them.

```
pip download <package>
```

Example:

```
pip download requests
```

## pip - List Installed Packages

List all the packages currently installed by pip.

```
pip list
```

## pip - Freeze Installed Packages

Capture the currently installed packages and their versions into a file, useful for recreating an environment.

```
pip freeze > requirements.txt
```

## pip - Install Packages from a Requirements File

Install all the packages specified in a `requirements.txt` file.

```
pip install -r requirements.txt
```

## pip - Install from a Custom Index

Install a package from an alternative index (not PyPI).

```
pip install --index-url <index_url> <package>
```

Example:

```
pip install --index-url https://our-pypi-proxy.internal.example.com requests
```

## pip - Install from an Extra Index

Install a package using an additional index (for local, unpublished packages).

```
pip install --extra-index-url <index_url> <package>
```

Example:

```
pip install --extra-index-url https://local-packages.internal.example.com requests
```

## pip - Install a Specific Version

Install a specific version of a package.

```
pip install <package>==<version>
```

Example:

```
pip install requests==2.22.0
```

## pip - Install a Version in a Range

Install the latest version of a package that falls within a specific version range.

```
pip install <package>>=<min_version>,<max_version>
```

Example:

```
pip install requests>=2.22.0,<3
```

## pip - Avoid a Specific Version

Install a package, but avoid a particular version.

```
pip install <package>!=<version_to_avoid>
```

Example:

```
pip install requests!=2.21.0
```

## pip - Create Wheels

Generate wheel files for a package and its dependencies and store them in a specified directory.

```
pip wheel --wheel-dir <directory> <package>
```

Example:

```
pip wheel --wheel-dir ./wheelhouse requests
```

Generate wheels for all packages in a requirements file and store them in a directory.

```
pip wheel --wheel-dir <directory> -r requirements.txt
```

Example:

```
pip wheel --wheel-dir ./wheelhouse -r requirements.txt
```

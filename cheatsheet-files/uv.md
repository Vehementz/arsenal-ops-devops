# uv

uv is an extremely fast Python package and project manager written in Rust. It replaces pip, pip-tools, pipx, virtualenv, and pyenv with a single tool, and resolves and installs dependencies from a lockfile.

#platform/multiple #target/Python #cat/PackageManagement

% uv, python, package management, virtualenv, lockfile

## uv - Initialize a Project

Create a new project with a `pyproject.toml`, a README, and a sample module.

```
uv init myproject
```

Initialize in the current directory instead, without creating sample files:

```
uv init --bare
```

## uv - Add a Dependency

Add a package to `pyproject.toml`, resolve it, and update `uv.lock`.

```
uv add requests
```

Pin a version constraint:

```
uv add 'django>=5.0,<6'
```

## uv - Add a Development Dependency

Add a package to the `dev` dependency group, excluded from production installs.

```
uv add --dev pytest ruff
```

Add to a named group instead:

```
uv add --group docs mkdocs
```

## uv - Remove a Dependency

Drop a package from `pyproject.toml` and re-lock the environment.

```
uv remove requests
```

## uv - Sync the Environment

Install exactly what `uv.lock` specifies, removing anything not in the lockfile. This is the reproducible install used in CI.

```
uv sync
```

Install without the dev dependencies:

```
uv sync --no-dev
```

Fail if the lockfile is out of date rather than updating it:

```
uv sync --locked
```

## uv - Update the Lockfile

Resolve dependencies and write `uv.lock` without installing anything.

```
uv lock
```

Upgrade every package to the newest allowed version:

```
uv lock --upgrade
```

Upgrade a single package only:

```
uv lock --upgrade-package requests
```

## uv - Run a Command in the Project

Run a command inside the project environment, syncing it first if needed. No manual activation required.

```
uv run python main.py
```

Run an installed tool:

```
uv run pytest -v
```

Run a script with inline dependencies, without a project:

```
uv run --with httpx script.py
```

## uv - Create a Virtual Environment

Create a `.venv` in the current directory.

```
uv venv
```

Create it with a specific Python version and path:

```
uv venv --python 3.12 .venv-3.12
```

## uv - Install Packages with the pip Interface

Use uv as a drop-in pip replacement against the active environment.

```
uv pip install requests
```

Install from a requirements file:

```
uv pip install -r requirements.txt
```

Install the current project in editable mode:

```
uv pip install -e .
```

## uv - Compile and Sync Requirements

Resolve `requirements.in` into a fully pinned `requirements.txt`, replacing pip-tools.

```
uv pip compile requirements.in -o requirements.txt
```

Install exactly that set, removing anything else:

```
uv pip sync requirements.txt
```

## uv - Manage Python Versions

Download and install a standalone Python interpreter.

```
uv python install 3.12
```

List the interpreters uv can see:

```
uv python list
```

Pin the version for this project, writing `.python-version`:

```
uv python pin 3.12
```

## uv - Install and Run Tools

Install a command-line tool into its own isolated environment, like pipx.

```
uv tool install ruff
```

Run a tool once without installing it:

```
uvx ruff check .
```

List installed tools:

```
uv tool list
```

## uv - Inspect the Dependency Tree

Show the resolved dependency tree for the project.

```
uv tree
```

Show only what depends on a given package:

```
uv tree --invert --package certifi
```

## uv - Export the Lockfile

Convert `uv.lock` into a `requirements.txt` for tools that cannot read it.

```
uv export --format requirements-txt -o requirements.txt
```

## uv - Build and Publish a Package

Build source and wheel distributions into `dist/`.

```
uv build
```

Publish the built distributions:

```
uv publish
```

## uv - Manage the Cache

Show where uv stores its cache.

```
uv cache dir
```

Remove cache entries that are no longer reachable:

```
uv cache prune
```

Clear the cache entirely:

```
uv cache clean
```

## uv - Update uv Itself

Update a standalone uv installation in place.

```
uv self update
```

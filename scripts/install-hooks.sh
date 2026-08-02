#! /bin/bash
# Point git at the version-controlled hooks in .githooks/.
# Hooks are not copied, so future updates to them apply automatically.

set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
chmod +x "$repo_root/.githooks/"* "$repo_root/scripts/"*.sh "$repo_root/scripts/"*.py
git -C "$repo_root" config core.hooksPath .githooks

echo "core.hooksPath -> .githooks (pre-commit lints staged cheatsheets)"

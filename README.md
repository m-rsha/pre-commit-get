# pre-commit-get

Manage your `pre-commit` hooks using an `apt`-like interface.
Add, remove, and search through all hooks listed on https://pre-commit.com/ to find the ones you need.

## **Attention: This tool is incomplete!**

`update`, `list`, `list --installed`, and `search` are the only working commands right now.

The code is also a bit of a spooky mess, just in time for Halloween! Read it at your own peril! D:

## examples

```console
# `update` downloads the hooks file from pre-commit
$ pre-commit-get update
Hook list updated, beep boop.

# List all available hooks
$ pre-commit-get list
... # Big ole list of hooks!

$ pre-commit-get list --installed
Installed hooks:
  trailing-whitespace (https://github.com/pre-commit/pre-commit-hooks)
  reorder-python-imports (https://github.com/asottile/reorder_python_imports)
  add-trailing-comma (https://github.com/asottile/add-trailing-comma)
  flake8 (https://github.com/PyCQA/flake8)
  mypy (https://github.com/pre-commit/mirrors-mypy)

# Search through all available hooks
$ pre-commit-get search reorder
reorder-python-imports: This hook reorders imports in python files. (https://github.com/asottile/reorder_python_imports)
cheetah-reorder-imports: This hook reorders imports in cheetah files. (https://github.com/asottile/cheetah_lint)

# `add` also has an "install" alias
$ pre-commit-get add reorder-python-imports
Hook added: reorder-python-imports

# `remove` also has an "uninstall" alias
$ pre-commit-get remove flake8
Hook removed: flake8
```

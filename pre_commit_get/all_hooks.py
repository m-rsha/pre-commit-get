from __future__ import annotations

import json
import os
import shutil
import sys
import urllib.request
from typing import Any

from pre_commit_get.schema import Hook
from pre_commit_get.schema import InstalledHook
# from pre_commit_get.hook import Hook


ALL_HOOKS = 'all-hooks.json'
ALL_HOOKS_URL = 'https://pre-commit.com/' + ALL_HOOKS
CACHE_DIR = '~/.cache/pre-commit-get'


def _create_cache_files():
    return


def _get_all_hooks_file() -> str:
    return os.path.join(os.path.expanduser(CACHE_DIR), ALL_HOOKS)


def get_all_hooks_json() -> dict[str, Any]:
    all_hooks = _get_all_hooks_file()
    try:
        with open(all_hooks, encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        raise SystemExit(f'Unable to find hooks file. \nTry running `{sys.argv[0]} update`')  # noqa: E501

    return data


def get_all_hooks() -> list[InstalledHook]:
    data = get_all_hooks_json()
    all_hooks = []
    for src, hooks in data.items():
        for hook in hooks:
            # hook = InstalledHook.create(hook, src=src)
            hook = Hook.create(hook, src=src)
            all_hooks.append(hook)

    return all_hooks


def update_hook_list() -> int:
    # TODO: Figure out how to embed the program version inside the user-agent
    # Use the importlib metadata recommendation on the python packaging site
    cache_dir = os.path.expanduser(CACHE_DIR)
    if not os.path.exists(cache_dir):
        os.mkdir(cache_dir)
    cache_file = _get_all_hooks_file()

    # TODO: Error handling
    req = urllib.request.Request(
        ALL_HOOKS_URL, headers={'User-Agent': 'pre-commit-get v0.0.2'},
    )
    with urllib.request.urlopen(req) as response:
        with open(cache_file, 'wb') as f:
            shutil.copyfileobj(response, f)

    print('Hook list updated, beep boop.')

    return 0


def search_hooks(hook_name_parts: list[str]) -> int:
    all_hooks = get_all_hooks()
    matching_hooks = []

    for hook in all_hooks:
        if all(part in hook.id for part in hook_name_parts):
            matching_hooks.append(hook)

    if len(matching_hooks) == 0:
        not_found = ', '.join(part for part in hook_name_parts)
        raise SystemExit(f"Hook(s) not found: '{not_found}'\nTry checking your spelling or updating your hook list with `{sys.argv[0]} update`.")  # noqa: E501

    for hook in matching_hooks:
        print(hook.id)

    return 0


def list_all_hooks() -> int:
    all_hooks = get_all_hooks()
    for hook in all_hooks:
        # TODO: Figure out f-strings matter. They look neat, right?
        print(f'{hook.id}')

    return 0

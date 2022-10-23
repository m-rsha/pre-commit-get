from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from typing import Any
from typing import NamedTuple
from typing import Sequence
from typing import TextIO

import yaml

from pre_commit_get.hook import Hook

SafeLoader = getattr(yaml, 'CSafeLoader', yaml.SafeLoader)
SafeDumper = getattr(yaml, 'CSafeDumper', yaml.SafeDumper)

ALL_HOOKS = 'all-hooks.json'
ALL_HOOKS_URL = 'https://pre-commit.com/all-hooks.json'

CONFIG = '.pre-commit-config.yaml'
TEST_CONFIG = 'test-config.yaml'


def yaml_load(o: Any) -> dict[str, Any]:
    return yaml.load(o, Loader=SafeLoader)


def yaml_dump(o: Any, stream: TextIO = sys.stdout) -> None:
    # TODO: Triple check how `default_flow_style` looks
    yaml.dump(o, stream, Dumper=SafeDumper, sort_keys=False, indent=4)


class Config(NamedTuple):
    data: dict[Any, Any]

    @classmethod
    def load(cls, cfg: str = CONFIG) -> Config:
        try:
            with open(cfg, encoding='utf-8') as f:
                yaml_file = yaml_load(f)
        except FileNotFoundError as e:
            raise SystemExit(f'Unable to find pre-commit config: {e}')

        return cls(yaml_file)

    def get_hooks(self) -> list[Hook]:
        hooks = []
        for repo in self.data['repos']:
            for hook in repo['hooks']:
                hooks.append(Hook.create(hook, src=repo['repo']))

        return hooks

    def _add_hook(self, hook: dict[Any, Any]) -> int:
        # TODO: Actually installll, derp.
        for repo in self.data['repos']:
            for _hook in repo['hooks']:
                if hook['id'] in _hook['id']:
                    raise SystemExit(f'Error: Hook already installed: {_hook["id"]}')  # noqa: E501

        return 0

    def _add_hook_by_name(self, name: str):
        print('aaaaa make dis stuff work')
        return

    def add_hooks(self, hook_names: list[str]) -> int:
        all_hooks = get_all_hooks_json()
        matches = []

        for hook_name in hook_names:
            self._add_hook_by_name(hook_name)

        for src, repos in all_hooks.items():
            for hook in repos:
                hook_id = hook['id']
                if all(name in hook_id for name in hook_names):
                    if any(name == hook_id for name in hook_names):
                        self._add_hook(hook)
                    else:
                        matches.append(hook)

        for match in matches:
            print(match['id'])

        return 0

    def _remove_repos_with_no_hooks(self) -> None:
        for repo in self.data['repos']:
            if len(repo['hooks']) == 0:
                self.data['repos'].remove(repo)

    def remove_hooks(self, hook_names: list[str]) -> int:
        for repo in self.data['repos']:
            for hook in repo['hooks']:
                for hook_name in hook_names:
                    if hook_name in hook['id']:
                        print(f'Hook removed: {hook["id"]}')
                        repo['hooks'].remove(hook)

        self._remove_repos_with_no_hooks()
        return 0


def get_all_hooks_json() -> dict[str, Any]:
    try:
        with open(ALL_HOOKS, encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        raise SystemExit(f'Unable to find hooks file. \nTry running `{sys.argv[0]} update`')  # noqa: E501

    return data


def get_all_hooks() -> list[Hook]:
    data = get_all_hooks_json()
    all_hooks = []
    for src, hooks in data.items():
        for hook in hooks:
            hook = Hook.create(hook, src=src)
            all_hooks.append(hook)

    return all_hooks


def update_hook_list() -> int:
    # TODO: Figure out how to embed the program version inside the user-agent
    cache_dir = os.path.join(os.path.expanduser('~/.cache'), 'pre-commit-get')
    if not os.path.exists(cache_dir):
        os.mkdir(cache_dir)
    cache_file = os.path.join(cache_dir, ALL_HOOKS)
    req = urllib.request.Request(
        ALL_HOOKS_URL, headers={'User-Agent': 'pre-commit-get v0.0.1'},
    )
    with urllib.request.urlopen(req) as response:
        with open(cache_file, 'wb') as f:
            f.write(response.read())

    print('Hook list updated, beep boop.')

    return 0


def list_hooks(hook_name_parts: list[str]) -> int:
    all_hooks = get_all_hooks()
    matching_hooks = []

    for hook in all_hooks:
        if all(part in hook.id for part in hook_name_parts):
            matching_hooks.append(hook)

    if len(matching_hooks) == 0:
        not_found = ', '.join(part for part in hook_name_parts)
        sys.stderr.write(f"Hook(s) not found: '{not_found}'\nTry checking your spelling or updating your hook list with `{sys.argv[0]} update`.\n")  # noqa: E501
        return 1

    for hook in matching_hooks:
        if hook.description is not None:
            print(f'{hook.id}: {hook.description} ({hook.src})')
        else:
            print(f'{hook.id} ({hook.src})')

    return 0


def list_all_hooks() -> int:
    all_hooks = get_all_hooks()
    for hook in all_hooks:
        print(f'{hook.id}')

    return 0


def main(argv: Sequence[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(
        description='Install hooks for pre-commit',
    )

    subparsers = parser.add_subparsers(dest='subcommand')

    subparsers.add_parser(
        'add', aliases=['install'],
        help='Install a pre-commit hook by adding it to your .pre-commit-config.yaml file',  # noqa: E501
    ).add_argument('HOOK_NAMES', nargs='+')

    subparsers.add_parser(
        'update', help='Update the list of available pre-commit hooks',
    )

    subparsers.add_parser(
        'remove', aliases=['uninstall'],
        help='Remove a hook from your .pre-commit-config.yaml file',
    ).add_argument('HOOK_NAMES', nargs='+')

    subparsers.add_parser(
        'search', help='Search for a pre-commit hook',
    ).add_argument('HOOK_NAME', nargs='+')

    subparsers.add_parser(
        'list',
        help='List all available pre-commit hooks',
    ).add_argument(
        '--installed', help='Show installed hooks', action='store_true',
    )

    args = parser.parse_args(args=argv)

    if args.subcommand is None:
        parser.print_help()
        return 0
    elif args.subcommand == 'update':
        return update_hook_list()
    elif args.subcommand == 'list' and not args.installed:
        return list_all_hooks()
    elif args.subcommand == 'search':
        return list_hooks(args.HOOK_NAME)

    config = Config.load()
    if args.subcommand in ('add', 'install'):
        return config.add_hooks(args.HOOK_NAMES)
    elif args.subcommand in ('remove', 'uninstall'):
        return config.remove_hooks(args.HOOK_NAMES)
    elif args.subcommand == 'list' and args.installed:
        hooks = config.get_hooks()
        print('Installed hooks:')
        for hook in hooks:
            if hook.description is not None:
                print(f'  {hook.id}: {hook.description} ({hook.src})')
            else:
                print(f'  {hook.id} ({hook.src})')
        return 0

    return 0


if __name__ == '__main__':
    raise SystemExit(main())

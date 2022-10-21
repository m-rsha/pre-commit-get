from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from typing import Any
from typing import NamedTuple
from typing import TextIO

import yaml


ALL_HOOKS = 'all-hooks.json'
ALL_HOOKS_URL = 'https://pre-commit.com/all-hooks.json'

CONFIG = '.pre-commit-config.yaml'
TEST_CONFIG = 'test-config.yaml'


class Hook(NamedTuple):
    src: str
    id: str
    name: str | None
    description: str | None
    args: list[str] | None

    @classmethod
    def create(cls, d: dict[Any, Any], *, src: str) -> Hook:
        return cls(
            src,
            d['id'],
            d.get('name'),
            d.get('description'),
            d.get('args'),
        )


class Config(NamedTuple):
    data: dict[Any, Any]

    @classmethod
    def load(cls, cfg: str = CONFIG) -> Config:
        yaml_file = {}
        try:
            with open(cfg, 'r', encoding='utf-8') as f:
                yaml_file = yaml.safe_load(f)
        except FileNotFoundError as e:
            sys.stderr.write(f'Unable to find pre-commit config: {e}\n')
            raise SystemExit(1)

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
                    sys.stdout.write(f'Error: Hook already installed: {_hook["id"]}\n')  # noqa: E501
                    raise SystemExit(1)

        return 0

    def add_hooks(self, hook_names: list[str]) -> int:
        all_hooks = get_all_hooks_json()
        for src, repos in all_hooks.items():
            for hook in repos:
                for hook_name in hook_names:
                    # Perfect match: add
                    if hook_name == hook['id']:
                        self._add_hook(hook)
                    # Imperfect match: Heck you
                    if hook_name in hook['id']:
                        print(hook['id'])

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


def yaml_dump(o: Any, stream: TextIO = sys.stdout) -> None:
    yaml.safe_dump(o, stream, sort_keys=False, indent=4)


def get_all_hooks_json() -> dict[str, Any]:
    try:
        with open(ALL_HOOKS, encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        raise SystemExit(f'Unable to find hooks file. \nTry running `{sys.argv[0]} update`\n')  # noqa: E501

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
    # TODO: Find an area in the home directory to store the hook list.
    req = urllib.request.Request(
        ALL_HOOKS_URL, headers={'User-Agent': 'pre-commit-get.py v0.0.1'},
    )
    with urllib.request.urlopen(req) as r:
        with open(ALL_HOOKS, 'w', encoding='utf-8') as f:
            f.writelines(line.decode() for line in r.readlines())

    print('Hook list updated, beep boop.')

    return 0


def list_hooks(hook_name_parts: list[str]) -> int:
    all_hooks = get_all_hooks()
    # TODO: Return only matches where all hook_name_parts are in hook.id
    matching_hooks = set()

    for hook in all_hooks:
        for part in hook_name_parts:
            if part in hook.id:
                matching_hooks.add(hook)

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


def main() -> int:
    argv = sys.argv[1:]
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
    if args.subcommand == 'add':
        return config.add_hooks(args.HOOK_NAMES)
    elif args.subcommand == 'remove':
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

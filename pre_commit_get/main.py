from __future__ import annotations

import argparse
import sys
from typing import Sequence

from pre_commit_get.all_hooks import list_all_hooks
from pre_commit_get.all_hooks import search_hooks
from pre_commit_get.all_hooks import update_hook_list
from pre_commit_get.schema import Config
# from pre_commit_get.config import Config


CONFIG = '.pre-commit-config.yaml'


def list_installed_hooks(config: Config) -> int:
    hooks = config.get_hooks()
    for hook in hooks:
        print(hook.id)

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
        return search_hooks(args.HOOK_NAME)

    config = Config.load(CONFIG)
    if args.subcommand in ('add', 'install'):
        return config.add_hooks(args.HOOK_NAMES)
    elif args.subcommand in ('remove', 'uninstall'):
        return config.remove_hooks(args.HOOK_NAMES)
    elif args.subcommand == 'list' and args.installed:
        return list_installed_hooks(config)

    return 0


if __name__ == '__main__':
    raise SystemExit(main())

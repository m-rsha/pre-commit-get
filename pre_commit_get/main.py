from __future__ import annotations

import argparse
import sys
from typing import Sequence

from pre_commit_get.all_hooks import list_all_hooks
from pre_commit_get.all_hooks import search_hooks
from pre_commit_get.all_hooks import update_hook_list
from pre_commit_get.config import get_config
from pre_commit_get.config import add_hook
from pre_commit_get.config import remove_hook
from pre_commit_get.config import get_installed_hooks


def main(argv: Sequence[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(
        description='Install hooks for pre-commit',
    )

    subparsers = parser.add_subparsers(dest='subcommand')

    subparsers.add_parser(
        'install',
        help='Install a pre-commit hook by adding it to your .pre-commit-config.yaml file',  # noqa: E501
    ).add_argument('HOOK_NAMES', nargs='+')

    subparsers.add_parser(
        'update', help='Update the list of available pre-commit hooks',
    )

    subparsers.add_parser(
        'uninstall',
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

    if args.subcommand == 'install':
        for hook_name in args.HOOK_NAMES:
            add_hook(hook_name)
        return 0
    elif args.subcommand == 'uninstall':
        for hook_name in args.HOOK_NAMES:
            remove_hook(hook_name)
        return 0
    elif args.subcommand == 'list' and args.installed:
        for installed_hook in get_installed_hooks():
            print(installed_hook)
        return 0

    return 0


if __name__ == '__main__':
    raise SystemExit(main())

from __future__ import annotations

from typing import Any
from typing import Literal
from typing import NamedTuple

import yaml

SafeLoader = getattr(yaml, 'CSafeLoader', yaml.SafeLoader)
SafeDumper = getattr(yaml, 'CSafeDumper', yaml.SafeDumper)

VALID_HOOK_TYPES = frozenset((
    'pre-commit', 'pre-merge-commit', 'pre-push', 'prepare-commit-msg',
    'commit-msg', 'post-checkout', 'post-commit', 'post-merge', 'post-rewrite',
))

STAGES = frozenset((
    'commit', 'merge-commit', 'push', 'prepare-commit-msg', 'commit-msg',
    'post-checkout', 'post-commit', 'post-merge', 'post-rewrite', 'manual',
))


# These are the same hooks in all-hooks.json and .pre-commit-hooks.yaml
# https://pre-commit.com/#creating-new-hooks
class Hook(NamedTuple):
    src: str
    id: str
    name: str
    entry: str
    language: str
    additional_dependencies: list[str] = []  # Not in the spec q.q
    files: str | None = ''
    exclude: str | None = '^$'
    types: list[str] = ['file']
    types_or: list[str] = []
    exclude_types: list[str] = []
    always_run: bool = False
    fail_fast: bool = False
    verbose: bool = False
    pass_filenames: bool = True
    require_serial: bool = False
    description: str = ''
    language_version: str | None = None  # 'default' ?
    minimum_pre_commit_version: str = '0'
    args: list[str] = []
    stages: list[str] = list(STAGES)

    @classmethod
    def create(cls, d: dict[Any, Any], src: str) -> Hook:
        return cls(src=src, **d)


class InstalledHook(NamedTuple):
    src: str
    id: str
    alias: str | None = None
    name: str | None = None
    language_version: str | None = None
    files: str | None = None
    exclude: str | None = None
    types: list[str] | None = None
    types_or: list[str] | None = None
    exclude_types: list[str] | None = None
    args: list[str] | None = None
    stages: list[str] | None = None
    additional_dependencies: list[str] | None = None
    always_run: bool | None = None  # presumably default 'false'
    verbose: bool | None = None  # presumably default 'false'
    log_file: str | None = None

    @classmethod
    def create(cls, d: dict[Any, Any], src: str) -> InstalledHook:
        return cls(src=src, **d)


class Repo(NamedTuple):
    repo: str  # also called 'src' by anthonk
    rev: str
    hooks: list[dict[Literal['hooks'], InstalledHook]]

    def get_hooks(self) -> list[InstalledHook]:
        hooks = []
        for hook in self.hooks:
            hooks.append(InstalledHook.create(**hook, src=self.repo))
        return hooks

    @classmethod
    def create(cls, d: dict[Any, Any]) -> Repo:
        return cls(**d)


class Config(NamedTuple):
    repos: dict[Literal['repos'], list[Repo]]
    default_install_hook_types: list[str] | None = ['pre-commit']
    default_language_version: dict[Any, Any] | None = {}
    default_stages: list[str] | None = None  # default all stages
    files: str | None = ''
    exclude: str | None = '^$'
    fail_fast: bool | None = False
    minimum_pre_commit_version: str | None = '0'

    def get_repos(self) -> list[Repo]:
        repos = []
        for repo in self.repos:
            repos.append(Repo.create(**repo))
        return repos

    def get_hooks(self) -> list[InstalledHook]:
        hooks = []
        for repo in self.get_repos():
            for hook in repo.get_hooks():
                hooks.append(hook)
        return hooks

    def add_hooks(self, hooks: list[str]):
        pass

    def remove_hooks(self, hooks: list[str]):
        pass

    @classmethod
    def _validate(cls, cfg: dict[str, Any]) -> None:
        for repo in cfg['repos']:
            for hook in Repo.create(**repo).hooks:
                InstalledHook.create(**hook, src=repo['repo'])

        if cfg.get('default_install_hook_types') is not None:
            for hook_type in cfg['default_install_hook_types']:
                if hook_type not in VALID_HOOK_TYPES:
                    raise SystemExit(f'Invalid hook type in `default_install_hook_types:` {hook_type}')  # noqa: E501

    @classmethod
    def load(cls, config_file: str) -> Config:
        with open(config_file, encoding='utf-8') as f:
            cfg = yaml.load(f, Loader=SafeLoader)

        # cls._validate(cfg)

        return cls(**cfg)

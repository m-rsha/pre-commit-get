from __future__ import annotations

from typing import Any
from typing import TextIO

import sys
import yaml

from pre_commit_get import constants as C


def yaml_load(o: Any) -> dict[Any, Any]:
    return yaml.load(
        o, Loader=getattr(yaml, 'CSafeLoader', yaml.SafeLoader)
    )


def yaml_dump(o: Any, stream: TextIO) -> dict[Any, Any]:
    return yaml.dump(
        o, stream, sort_keys=False,
        Dumper=getattr(yaml, 'CSafeDumper', yaml.SafeDumper)
    )


def get_config(cfg_file: str = C.CONFIG) -> dict[Any, Any]:
    with open(cfg_file, encoding='utf-8') as f:
        return yaml_load(f)


def add_hook(hook_name: str) -> int:
    return 0


def remove_hook(hook_name: str) -> int:
    cfg = get_config()
    for repos in cfg.values():
        for idx, repo in enumerate(repos):
            for hook in repo['hooks']:
                if hook_name == hook['id']:
                    repo = cfg['repos'][idx]
                    hooks = cfg['repos'][idx]['hooks']
                    to_remove = hook
                    break

    hooks.remove(to_remove)
    if len(hooks) == 0:
        cfg['repos'].remove(repo)
    yaml_dump(cfg, sys.stdout)

    return 0


def get_installed_hooks() -> list[str]:
    hooks = []
    for repos in get_config().values():
        for repo in repos:
            for hook in repo['hooks']:
                hooks.append(hook['id'])
    return hooks

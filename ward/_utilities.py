import asyncio
import collections
import inspect
from pathlib import Path
from typing import Any, Callable, Dict, Hashable, Iterable, List, Optional, TypeVar


def truncate(s: str, num_chars: int) -> str:
    suffix = "..." if len(s) > num_chars else ""
    return s[: num_chars - len(suffix)] + suffix


def find_project_root(paths: Iterable[Path]) -> Optional[Path]:
    if not paths:
        return None

    common_base = min(path.resolve() for path in paths)
    if common_base.is_dir():
        common_base /= "child-of-base"

    # Check this common base and all of its parents for files
    # indicating the project root
    for directory in common_base.parents:
        if (directory / "pyproject.toml").is_file():
            return directory
        if (directory / ".git").exists():
            return directory
        if (directory / ".hg").is_dir():
            return directory

    return None


def get_absolute_path(object: Any) -> Path:
    return Path(inspect.getfile(object)).absolute()


T = TypeVar("T")
H = TypeVar("H", bound=Hashable)


def group_by(items: Iterable[T], key: Callable[[T], H]) -> Dict[H, List[T]]:
    groups = collections.defaultdict(list)
    for item in items:
        groups[key(item)].append(item)
    return dict(groups)


def get_current_event_loop() -> asyncio.AbstractEventLoop:
    """
    Try to get the current asyncio event loop.
    If no loop is available or the current loop is closed,
    creates a new asyncio event loop and sets it as the current loop.
    """
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            return _create_new_event_loop()

        if not loop.is_closed():
            return loop

        return _create_new_event_loop()


def _create_new_event_loop() -> asyncio.AbstractEventLoop:
    """
    Creates a new asyncio event loop and sets it as the current loop.
    Should be used it with caution, as it may interfere in ASGI apps.
    Should only be used when absolutely no loop is available or the current loop is closed.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop

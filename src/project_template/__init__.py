"""Placeholder package for BearingQuest projects."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("project-template")
except PackageNotFoundError:  # pragma: no cover - only when run from an uninstalled source tree
    __version__ = "0.0.0"

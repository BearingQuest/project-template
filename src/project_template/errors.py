"""Typed errors. The CLI maps these to a plain message and a non-zero exit."""


class ProjectTemplateError(Exception):
    """Base class for every error this package raises on purpose."""


class ConfigError(ProjectTemplateError):
    """A setting is missing or invalid."""


class InputError(ProjectTemplateError):
    """A caller supplied invalid input."""

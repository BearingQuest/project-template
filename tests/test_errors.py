import pytest

from project_template.errors import ConfigError, InputError, ProjectTemplateError


@pytest.mark.parametrize("error", [ConfigError, InputError])
def test_specific_errors_are_project_template_errors(error: type[ProjectTemplateError]) -> None:
    assert issubclass(error, ProjectTemplateError)
    assert str(error("boom")) == "boom"


def test_the_specific_errors_are_distinct() -> None:
    assert not issubclass(ConfigError, InputError)
    assert not issubclass(InputError, ConfigError)

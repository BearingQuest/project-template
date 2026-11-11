import pytest

from project_template.core.greeting import greet
from project_template.errors import InputError


def test_greets_a_valid_name() -> None:
    assert greet("Ada", 50) == "Hello, Ada!"


def test_strips_surrounding_whitespace() -> None:
    assert greet("  Ada  ", 50) == "Hello, Ada!"


@pytest.mark.parametrize("name", ["", "   ", "\t\n"])
def test_rejects_an_empty_name(name: str) -> None:
    with pytest.raises(InputError, match="empty"):
        greet(name, 50)


def test_length_limit_is_inclusive() -> None:
    assert greet("a" * 5, 5) == "Hello, aaaaa!"
    with pytest.raises(InputError, match="at most 5"):
        greet("a" * 6, 5)


def test_rejects_control_characters() -> None:
    with pytest.raises(InputError, match="printable"):
        greet("Ada\x1b[31m", 50)

import pytest

from project_template.config import Settings, load_settings
from project_template.errors import ConfigError


@pytest.fixture(autouse=True)
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PT_LOG_LEVEL", raising=False)
    monkeypatch.delenv("PT_MAX_NAME_LENGTH", raising=False)


def test_defaults() -> None:
    settings = load_settings()
    assert settings.log_level == "INFO"
    assert settings.max_name_length == 50


def test_environment_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PT_LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("PT_MAX_NAME_LENGTH", "10")
    settings = load_settings()
    assert (settings.log_level, settings.max_name_length) == ("DEBUG", 10)


def test_only_the_pt_prefix_is_read(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    assert load_settings().log_level == "INFO"


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("PT_LOG_LEVEL", "TRACE"),
        ("PT_LOG_LEVEL", "info"),
        ("PT_MAX_NAME_LENGTH", "0"),
        ("PT_MAX_NAME_LENGTH", "201"),
        ("PT_MAX_NAME_LENGTH", "many"),
    ],
)
def test_invalid_values_raise_config_error(
    monkeypatch: pytest.MonkeyPatch, name: str, value: str
) -> None:
    monkeypatch.setenv(name, value)
    with pytest.raises(ConfigError, match="invalid configuration"):
        load_settings()


def test_config_error_names_the_field_but_not_the_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PT_MAX_NAME_LENGTH", "s3cr3t-value")
    with pytest.raises(ConfigError) as info:
        load_settings()
    assert "max_name_length" in str(info.value)
    assert "s3cr3t-value" not in str(info.value)


def test_settings_are_frozen() -> None:
    settings = Settings()
    with pytest.raises(ValueError, match="frozen"):
        settings.log_level = "DEBUG"  # type: ignore[misc]

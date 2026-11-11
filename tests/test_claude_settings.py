"""AGENT-01..06: .claude/settings.json keeps every deny, ask and sandbox key, and allows nothing.

The only command excluded from the sandbox is gh.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SETTINGS = REPO_ROOT / ".claude" / "settings.json"
SCHEMA = "https://json.schemastore.org/claude-code-settings.json"

MODE_LOCKS = ["disableAutoMode", "disableBypassPermissionsMode"]

REQUIRED_DENY = [
    # gh pr merge, and the script that wraps it (the gh deny cannot see inside it)
    "Bash(gh pr merge *)",
    "Bash(gh * pr merge)",
    "Bash(gh * pr merge *)",
    "Bash(bq-merge *)",
    # force pushes, plain and option-first
    "Bash(git push --force*)",
    "Bash(git push -f*)",
    "Bash(git push * --force*)",
    "Bash(git push * -f*)",
    "Bash(git push * +*)",
    "Bash(git * push --force*)",
    "Bash(git * push -f*)",
    "Bash(git * push * --force*)",
    "Bash(git * push * -f*)",
    "Bash(git * push * +*)",
    # recursive force deletes
    "Bash(rm -rf *)",
    "Bash(rm -fr *)",
    "Bash(rm -r -f *)",
    "Bash(rm -f -r *)",
    "Bash(rm -Rf *)",
    "Bash(rm -fR *)",
    # terraform
    "Bash(terraform apply *)",
    "Bash(terraform * apply *)",
    "Bash(terraform destroy *)",
    "Bash(terraform * destroy *)",
    # repository, Actions, security and Pages settings, secrets, releases
    "Bash(gh api *rulesets*)",
    "Bash(gh api *actions/permissions*)",
    "Bash(gh api *code-security*)",
    "Bash(gh api *environments*)",
    "Bash(gh api *actions/secrets*)",
    "Bash(gh api *pages*)",
    "Bash(gh secret *)",
    "Bash(gh repo create *)",
    "Bash(gh repo edit *)",
    "Bash(gh release *)",
    # gh runs outside the sandbox, so nothing stops it printing its token but these
    "Bash(gh auth token*)",
    "Bash(gh auth status *--show-token*)",
    "Bash(gh auth status *-t*)",
    # tags
    "Bash(git tag *)",
    "Bash(git * tag)",
    "Bash(git * tag *)",
    "Bash(git push *--tags*)",
    "Bash(git * push *--tags*)",
    "Bash(git push *--follow-tags*)",
    "Bash(git * push *--follow-tags*)",
]

REQUIRED_READ_DENY = [
    "Read(~/.ai_post_env)",
    "Read(~/.aws/**)",
    "Read(~/.ssh/**)",
    "Read(~/.config/gh/**)",
    "Read(~/career-workspace/**)",
    "Read(./.env)",
    "Read(./.env.*)",
]

# Edit rules cover every built-in file-editing tool, Write included; Write(path)
# rules do not match anything, so the settings files are protected with Edit.
REQUIRED_EDIT_DENY = [
    "Edit(/.claude/settings.json)",
    "Edit(/.claude/settings.local.json)",
    "Edit(~/.claude/settings.json)",
    "Edit(//Library/Application Support/ClaudeCode/**)",
]

REQUIRED_ASK = [
    "Bash(git push *)",
    "Bash(git * push)",
    "Bash(git * push *)",
    "Bash(gh pr *)",
    "Bash(gh * pr)",
    "Bash(gh * pr *)",
    "Bash(gh api *)",
    "Bash(gh * api)",
    "Bash(gh * api *)",
    "Bash(python3 *)",
]

# gh cannot read its login in ~/.config/gh from inside the sandbox, so it runs
# outside it. The entry needs the trailing " *": a bare "gh" matches only `gh` with
# no arguments. Nothing else may be excluded; the deny and ask rules above still apply.
SANDBOX_EXCLUDED_COMMANDS = ["gh *"]

# Sandbox paths differ from Read()/Edit() rules: "/" is absolute, "~/" is home,
# "./" is the project root.
SANDBOX_FLAGS = {
    "enabled": True,
    "failIfUnavailable": True,
    "allowUnsandboxedCommands": False,
    "autoAllowBashIfSandboxed": False,
}

SANDBOX_DENY_READ = {
    "~/.ai_post_env",
    "~/.aws",
    "~/.ssh",
    "~/.config/gh",
    "~/career-workspace",
    "./.env",
    "./.env.*",
}

# An Edit() deny does not stop a shell redirect, so the settings files are
# also write-denied for sandboxed commands.
SANDBOX_DENY_WRITE = {
    "./.claude/settings.json",
    "./.claude/settings.local.json",
    "~/.claude/settings.json",
    "/Library/Application Support/ClaudeCode",
}

# uv's cache: `uv sync`, `uv run` and `uv export` write there. Python 3.14 is
# already installed under ~/.local/share/uv/python, so nothing else is needed.
SANDBOX_ALLOW_WRITE = {"~/.cache/uv"}

SANDBOX_ALLOWED_DOMAINS = {
    "pypi.org",  # dependency resolution and pip-audit lookups
    "files.pythonhosted.org",  # wheel downloads
    "github.com",
    "api.github.com",
}


@pytest.fixture(scope="module")
def settings() -> dict[str, Any]:
    data: dict[str, Any] = json.loads(SETTINGS.read_text(encoding="utf-8"))
    return data


def test_schema_is_declared(settings: dict[str, Any]) -> None:
    assert settings["$schema"] == SCHEMA


@pytest.mark.parametrize("key", MODE_LOCKS)
def test_mode_is_disabled(settings: dict[str, Any], key: str) -> None:
    assert settings["permissions"][key] == "disable"


@pytest.mark.parametrize("rule", REQUIRED_DENY)
def test_deny_rule_present(settings: dict[str, Any], rule: str) -> None:
    assert rule in settings["permissions"]["deny"]


def test_no_option_first_gh_auth_deny(settings: dict[str, Any]) -> None:
    # "Bash(gh * auth token*)" matches any gh command whose text mentions "auth token",
    # including `gh pr create` with that phrase in its title or body, so it silently
    # refuses legitimate calls. Only the plain "gh auth ..." forms may be denied.
    option_first = [
        rule
        for rule in settings["permissions"]["deny"]
        if rule.startswith("Bash(gh *") and "auth" in rule
    ]
    assert option_first == []


@pytest.mark.parametrize("rule", REQUIRED_READ_DENY)
def test_read_deny_rule_present(settings: dict[str, Any], rule: str) -> None:
    assert rule in settings["permissions"]["deny"]


@pytest.mark.parametrize("rule", REQUIRED_EDIT_DENY)
def test_edit_deny_rule_present(settings: dict[str, Any], rule: str) -> None:
    assert rule in settings["permissions"]["deny"]


@pytest.mark.parametrize("rule", REQUIRED_ASK)
def test_ask_rule_present(settings: dict[str, Any], rule: str) -> None:
    assert rule in settings["permissions"]["ask"]


@pytest.mark.parametrize(("key", "value"), SANDBOX_FLAGS.items())
def test_sandbox_flag(settings: dict[str, Any], key: str, value: bool) -> None:
    assert settings["sandbox"][key] is value


@pytest.mark.parametrize(
    ("section", "key", "expected"),
    [
        ("filesystem", "denyRead", SANDBOX_DENY_READ),
        ("filesystem", "denyWrite", SANDBOX_DENY_WRITE),
        ("filesystem", "allowWrite", SANDBOX_ALLOW_WRITE),
        ("network", "allowedDomains", SANDBOX_ALLOWED_DOMAINS),
    ],
)
def test_sandbox_list_is_exact(
    settings: dict[str, Any], section: str, key: str, expected: set[str]
) -> None:
    # Set equality: a path or host added without updating this test fails too.
    assert set(settings["sandbox"][section][key]) == expected


def test_sandbox_excluded_commands_is_exact(settings: dict[str, Any]) -> None:
    # List equality: any extra, missing or reordered entry fails.
    assert settings["sandbox"]["excludedCommands"] == SANDBOX_EXCLUDED_COMMANDS


def test_strict_allowlist_is_not_in_repo_file(settings: dict[str, Any]) -> None:
    # sandbox.network.strictAllowlist only takes effect from user or managed
    # settings, so a copy here would do nothing and look like protection.
    # Each developer sets it in ~/.claude/settings.json (see AGENTS.md).
    assert "strictAllowlist" not in settings["sandbox"]["network"]


def test_no_allow_rules(settings: dict[str, Any]) -> None:
    assert "allow" not in settings
    assert not settings["permissions"].get("allow")

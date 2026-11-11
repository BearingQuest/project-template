# Changelog

All notable changes to this project are recorded here, newest first.

## Unreleased

- Sandbox: `gh` runs outside it (`excludedCommands: ["gh *"]`) so it can read its login;
  new denies on `gh auth token`, `--show-token` and `-t`; test requires `gh` to be the only
  exclusion.
- Agent rules: shared `.claude/settings.json` (deny and ask rules, no allow rules, mode
  locks, `bq-merge` deny) with a sandbox pilot, and `tests/test_claude_settings.py`.
- Scaffold: `project_template` package with the `pt` Typer CLI, pydantic-settings
  configuration, structured JSON logging and typed errors.
- Local gates (`make check`, `make audit`, `make hooks`) and the five required CI
  jobs: `check`, `gitleaks`, `semgrep`, `pip-audit`, `zizmor`.
- Ruleset files for `main` and release tags, and the repository docs.

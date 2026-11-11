# Changelog

All notable changes to this project are recorded here, newest first.

## Unreleased

- Scaffold: `project_template` package with the `pt` Typer CLI, pydantic-settings
  configuration, structured JSON logging and typed errors.
- Local gates (`make check`, `make audit`, `make hooks`) and the five required CI
  jobs: `check`, `gitleaks`, `semgrep`, `pip-audit`, `zizmor`.
- Ruleset files for `main` and release tags, and the repository docs.

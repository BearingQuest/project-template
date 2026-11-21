# Changelog

All notable changes to this project are recorded here, newest first.

## Unreleased

- README family header, badges, demo GIF and diagram; tests/test_readme.py checks README images.
- Claude review: `claude_args` adds `--settings '{"sandbox":{"enabled":false}}'` so the review
  runs on a runner without bubblewrap or socat; the tool list is still the inline-comment tool
  alone, and a test requires both.
- Baseline 2.0 audit fixes: `AGENTS.md` tells the agent to run `gh` on its own and documents the
  sandbox-safe zizmor command; tests for both and for the ruff baseline block; `docs/decisions.md`
  records "Meets engineering baseline 2.0", the mutation check, the gitleaks rescan and the GH-02
  API defaults.
- Workflows: daily pip-audit, Dependabot (uv and github-actions), OpenSSF Scorecard and
  Claude review, none required; `release.yml` builds on a `v*` tag in a read-only job and
  opens a draft release with the wheel, sdist and SBOM, each with a build-provenance
  attestation, from a separate job; the notes are the tag's `CHANGELOG.md` section and the
  build fails without one.
- `make sbom`: CycloneDX SBOM of the locked runtime dependencies, with a test that no
  dev-group package appears in it.
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

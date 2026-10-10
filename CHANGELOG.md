# Changelog

## 0.2.0 - 2026-10-10

### Fixed

- Validate each redirect before contacting its target; reject host changes,
  HTTPS downgrades, alternate ports, and URL credentials.
- Handle interrupted HTTP responses through normal error reporting and
  same-commit mirror fallback without changing requested versions.
- Preserve partial output and failed-command records when SDK commands time
  out or cannot start.
- Include full licenses and attribution in every standalone skill copy.

### Added

- Offline `info` metadata, explicit multi-term AND search (`--match all`),
  next-page commands, and clearer CLI help; `url` no longer needs the catalog.
- Root-discoverable offline tests for catalog integrity, reference reachability,
  SDK diagnostics, redirects, concurrent caching, installation, and packaging.
- Non-overwriting Python installer for Codex, Cursor, Claude Code, and custom
  destinations; documented Continue rule bridge.
- Reproducible standalone ZIP and SHA-256 checksum, CI on Linux/macOS/Windows
  with Python 3.9 and 3.14, automatic tagged releases, and opt-in SDK workflow.
- Quick start, installation and update guidance, FAQ, changelog, ignore rules,
  stable line endings, and supported Codex icon/color/invocation metadata.

### Unchanged

- Audited documentation commit and Cangjie semantics; no new SDK compatibility
  claims, runtime dependencies, automatic SDK installation, or cache eviction.
- Literal phrase search remains the default; offline caches are retained.

## 0.1.0 - 2026-10-09

- Initial Cangjie skill, task-oriented references, 297-file documentation catalog,
  version-aware retrieval, and SDK 1.0.5 validation examples.

# Contributing to vesl-identity

Thanks for your interest. This workspace is under active development. Contributions are coordinated by the maintainers.

## Quick development setup

```bash
git clone https://github.com/zkvesl/vesl-identity.git
cd vesl-identity
cargo build --workspace
cargo test --workspace --all-features
cargo clippy --workspace --all-targets --all-features -- -D warnings
cargo fmt --all -- --check
cargo deny check
```

## Conventions

- **Crate naming**: `vesl-*` for crates published from this workspace.
- **MSRV**: `1.85`. Bumps require a CHANGELOG entry and CI matrix update.
- **License**: dual MIT / Apache-2.0. New files get the standard SPDX header on contribution.
- **Tests**: every public function has at least one test. Tests live alongside the code they exercise (`#[cfg(test)] mod tests { … }`).
- **Commits**: imperative-mood subject lines, ≤72 chars, body wrapped at 72 chars.
- **PRs**: rebased on `main`, CI green, no force-pushes after review starts.

## Reporting issues

Use the GitHub issue tracker. For security-sensitive reports, see `SECURITY.md` (when added).

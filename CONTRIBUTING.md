# Contributing to vesl-identity

Thanks for your interest. This workspace is in early-phase development (Phase 0 of the Vesl shared-infrastructure plan). Contributions during W1-3 (vesl-signing lift), W4-5 (vesl-wallet-spec), and W6-8 (vesl-wallet) are coordinated by the maintainers.

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
- **Tests**: every public function has at least one test. Lifted modules carry their own tests; new code adds new tests in the same file (`#[cfg(test)] mod tests { … }`).
- **Commits**: imperative-mood subject lines, ≤72 chars, body wrapped at 72 chars.
- **PRs**: rebased on `main`, CI green, no force-pushes after review starts.

## Reporting issues

Use the GitHub issue tracker. For security-sensitive reports, see `SECURITY.md` (when added).

## Code of conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

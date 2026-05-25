# Contributing to vesl-wallet

vesl-wallet is the three-crate workspace that backs every signing
flow against a Nockchain hull: Schnorr/Tip5 signing primitives in
`vesl-signing`, BIP-44 layout spec in `vesl-wallet-spec`, and the
HD wallet API in `vesl-wallet`. The crates are independent —
consumers can `cargo add vesl-signing` without pulling the HD layer
— and external contributions are welcome.

PRs land against the `main` branch. Branch off `main`, push to your
fork, open the PR against `zkvesl/vesl-wallet:main`. Until a `dev`
branch is opened here, every PR is reviewed against `main` directly.

## Good first PRs

The wallet workspace is small enough that the contribution surface
is mostly "add tests + examples + rustdoc that aren't there yet."
Three concrete shapes that take an hour or less:

| Add a... | Open this directory | Pattern |
|---|---|---|
| **Signing test vector** | `crates/vesl-signing/tests/vectors.rs` (create) | A reference test vector lets downstream consumers self-validate their integration without standing up a Hull. Pick a (seed, message, sig) triple from the Cheetah-over-Tip5 reference impl in `vesl-signing/src/` and assert the round-trip. |
| **Runnable example** | `crates/vesl-signing/examples/` or `crates/vesl-wallet/examples/` | `mock_trust_anchor.rs` is the existing template for vesl-signing. A "derive → sign → submit → verify" end-to-end for `vesl-wallet` is missing — high-value contribution. |
| **Rustdoc on a public item** | Any `crates/*/src/*.rs` | Run `cargo doc --no-deps --workspace` and look for `pub` items without a `///` line. Adding one doc-line per item with a usage example improves the `cargo doc --open` surface that downstream Rust consumers read. |

For larger work — new key-derivation paths, alternate signing
schemes, MSRV bumps — open a draft PR or an issue first so we can
coordinate the API shape.

## Running tests

```bash
# Full workspace test suite — incremental ~3s warm; first-clone cold
# build ~2 min.
cargo test --workspace --all-features

# Lint gates that CI enforces. Run these before pushing.
cargo clippy --workspace --all-targets --all-features -- -D warnings
cargo fmt --all -- --check

# Cargo-deny: license + advisory check. CI runs this as a hard gate.
cargo deny check
```

Per-crate test loops are faster when you're only touching one:

```bash
cargo test -p vesl-signing
cargo test -p vesl-wallet
cargo test -p vesl-wallet-spec
```

## CI and getting reviewed

PRs run four jobs (visible at the bottom of the PR conversation):

- **check-pins** — sub-second; validates `scripts/check-pins.sh` if
  configured.
- **test** — `cargo test --workspace --all-features --locked`
  against the MSRV matrix (`stable` + `1.85`).
- **lint** — `cargo fmt --check` + `cargo clippy --workspace
  --all-targets --all-features -- -D warnings`.
- **cargo-deny** — license, banned-crate, advisory, and source
  checks against `deny.toml`.

A clean run shows green checks across every job in <5 min. A red
job's "Details" link goes straight to the failing step's logs.
Re-run a flaky job from the PR page if needed.

**Reviewer routing.** Tag `@zkvesl` on the PR or in your description
if it sits open more than a day; we triage from there. Code owners
for the workspace are tracked in `.github/CODEOWNERS`.

For PRs touching `crates/vesl-signing/` (the cryptographic
primitives, including the Schnorr-over-Cheetah-over-Tip5 chain),
expect closer review — these primitives back every hull's signed
intent path.

## Conventions

- **Crate naming**: `vesl-*` for crates published from this workspace.
- **MSRV**: `1.85`. Bumps require a CHANGELOG entry and CI matrix update.
- **License**: dual MIT / Apache-2.0. New files get the standard
  SPDX header on contribution.
- **Tests**: every public function has at least one test. Tests live
  alongside the code they exercise (`#[cfg(test)] mod tests { … }`)
  or as integration tests under `crates/<name>/tests/`.
- **Commits**: imperative-mood subject lines, ≤72 chars, body
  wrapped at 72 chars.
- **PRs**: rebased on `main`, CI green, no force-pushes after
  review starts.

## Reporting issues

Use the GitHub issue tracker. For security-sensitive reports, see
`SECURITY.md` (when added) — until then, contact the maintainers
directly rather than opening a public issue.

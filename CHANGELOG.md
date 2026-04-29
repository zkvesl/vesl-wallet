# Changelog

All notable changes to this workspace are documented here. Each crate also tracks its own version in its `Cargo.toml`; the workspace tag tracks bundle milestones.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- (W1) Workspace scaffolding: root `Cargo.toml`, three placeholder crates (`vesl-signing`, `vesl-wallet-spec`, `vesl-wallet`), CI pipeline (`cargo test`, `cargo clippy`, `cargo fmt`, `cargo deny`), `LICENSE-{MIT,APACHE}`, `README.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `deny.toml`, `rust-toolchain.toml` (pinned `stable`).

### Pending

- **`SchnorrSignatureJson` ownership** with x402-types maintainer (Day 6).
- **`nockchain-math::CheetahPoint` coordinate API** verification (Day 14, only blocks Phase 6 of the lift).

### Resolved

- **GitHub org confirmation** (2026-04-29): `zkvesl/vesl-identity`. Matches existing convention with `zkvesl/x402-nockchain`, `zkvesl/vesl-core`, `zkvesl/hull-llm`.

## [0.0.0] — Scaffold

Initial workspace scaffold. No functional crates yet — `cargo build --workspace` and `cargo test --workspace` build green on three placeholder lib crates.

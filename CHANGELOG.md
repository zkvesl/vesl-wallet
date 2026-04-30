# Changelog

All notable changes to this workspace are documented here. Each crate also tracks its own version in its `Cargo.toml`; the workspace tag tracks bundle milestones.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added — `vesl-signing`

- **`vesl-signing` crate** lifted from `x402-nockchain/crates/x402-nockchain-crypto/`:
  - `schnorr.rs` — `SchnorrPrivateKey`, `schnorr_sign`, `schnorr_verify`, plus new `from_belts(&[Belt; 8])` / `to_belts() -> [Belt; 8]` constructors for the `vesl-core` shim path.
  - `domain.rs` (renamed from `canonical.rs`) — five reserved Tip5 domain separators: `X402`, `SIWN`, `VESL_INTENT`, `VESL_RECEIPT` (NEW, for receipt schema v2), `VESL_AUTHORITY` (NEW, for trust-anchor signed statements). Closes OD#2.
  - `replay_cache.rs` — `ReplayCache` trait + `InMemoryReplayCache`.
  - `caip122.rs` (renamed from `siwn.rs`) — generic CAIP-122 signing for non-x402 consumers; SIWN is the canonical example.
  - `prelude` module — curated `Belt` + `hash_varlen` re-export for downstream shim crates.
  - `math/` — vendored Goldilocks/Cheetah/Tip5/F6 substrate (`pub(crate)`, no upstream `nockchain-math` dep).
- Internal `SchnorrSignatureJson` / `SchnorrPair` wire types replace the previous `x402-types::payment::*` coupling. Gated behind feature `json`.
- Three feature gates: `json` (wire types), `siwn` (CAIP-122 module, requires `json`), default = `[json, siwn]`. Hardware-wallet vendors can opt in to a leaner profile via `default-features = false`.
- Integration test `tests/api_smoke.rs` — black-box smoke against the public API, guards against accidental private-symbol leaks.
- Example `examples/mock_trust_anchor.rs` — non-x402 SIWN consumer demonstrating the API generalizes beyond x402 (mocks a Hull Authority gate).
- Stub `tests/parity_with_nockchain_math.rs` — placeholder for the v0.2.0 parity-regen workflow (math drift detection against `nockchain-math` upstream).

### Verified — `vesl-signing`

- `cargo test --no-default-features`: 22 tests pass (lean profile, no JSON / SIWN).
- `cargo test --features json`: 36 tests pass (adds JSON wire-type tests + api_smoke).
- `cargo test --all-features`: 42 tests pass (adds caip122 SIWN tests).
- `cargo clippy --workspace --all-targets --all-features -- -D warnings`: clean.
- `cargo fmt --all -- --check`: clean.
- `cargo deny check`: clean.
- `cargo run --example mock_trust_anchor`: SIWN sign/verify/replay-reject end-to-end.

### Added — `vesl-wallet-spec`

- **`vesl-wallet-spec` crate** — doc-only canonical reference for the BIP44 5-level wallet layout used across the Vesl stack.
  - `SPEC.md` at the crate root: path shape, role assignments 0-4 (closes OD#1 with `role=4` reserved for x402 spending keys), domain-separator registry pointing at `vesl-signing`, SLIP-44 stance, BIP-style versioning policy.
  - `lib.rs` exports: `BIP44_PURPOSE` constant + five `ROLE_*` constants (`ROLE_INTENT`=0, `ROLE_RECEIVING`=1, `ROLE_ENCRYPTION`=2, `ROLE_SESSION`=3, `ROLE_X402`=4) + typed `DerivationPath` struct (no derivation logic — that lives in `vesl-wallet`).
  - Three crate-internal tests: constant stability, `DerivationPath` Eq/Hash contract, role-distinctness.

### Added — Workspace scaffolding

- Workspace scaffolding: root `Cargo.toml`, three placeholder crates (`vesl-signing`, `vesl-wallet-spec`, `vesl-wallet`), CI pipeline (`cargo test`, `cargo clippy`, `cargo fmt`, `cargo deny`), `LICENSE-{MIT,APACHE}`, `README.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `deny.toml`, `rust-toolchain.toml` (pinned `stable`).

### Pending

- **`SchnorrSignatureJson` ownership** with x402-types maintainer (vesl-signing currently owns the canonical wire type; x402-types will need to re-export or maintain a structurally-identical type with `From` impls).
- **`nockchain-math::CheetahPoint` coordinate API** verification.
- **v0.1.0 tag**: mint after end-to-end verification across `vesl-identity` / `vesl-core` / `vesl-nockup` / `x402-nockchain`.
- **v0.2.0**: `nockchain-math` parity-vector regen workflow; `SchnorrPrivateKey` zeroization (audit ref `vesl-core L-06`).

### Resolved

- **GitHub org confirmation** (2026-04-29): `zkvesl/vesl-identity`. Matches existing convention with `zkvesl/x402-nockchain`, `zkvesl/vesl-core`, `zkvesl/hull-llm`.

## [0.0.0] — Scaffold

Initial workspace scaffold. No functional crates yet — `cargo build --workspace` and `cargo test --workspace` build green on three placeholder lib crates.

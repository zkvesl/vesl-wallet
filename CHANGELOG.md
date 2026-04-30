# Changelog

All notable changes to this workspace are documented here. Each crate also tracks its own version in its `Cargo.toml`; the workspace tag tracks bundle release points.

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

### Added — `vesl-wallet`

- **`vesl-wallet` crate** — high-level Hull-author wallet API bundling BIP-39 seed handling + a custom Cheetah-BIP32-over-Tip5 HD layer + the `vesl-wallet-spec` BIP-44 layout into a single surface.
  - `hd.rs` — pure-Rust HD derivation. Master scalar + chain code derived from the 64-byte BIP-39 seed via Tip5 under the new [`VESL_HD`] separator (rather than HMAC-SHA512). Hardened CKD (parent private scalar in transcript) and non-hardened CKD (parent public point in transcript). Output expansion uses two domain-separated Tip5 calls (one for the scalar tweak, one for the chain code) keyed on `VESL_HD` + an inner subdomain literal.
  - `wallet.rs` — `VeslWallet` API: `from_seed_phrase(phrase, passphrase, coin_type)`, `from_seed(seed, coin_type)`, `derive(path)`, plus per-role conveniences `sign_intent`, `receiving_pubkey`, `receiving_fingerprint`, `derive_session`, `intent_signer`, `payment_signer`. The `intent_signer` / `payment_signer` split is the entry point for the TOML config-toggle pattern (same code, different role).
  - `error.rs` — `WalletError` enum (invalid mnemonic, scalar reduction failure, BIP-44 purpose mismatch, hardened-index overflow, transparent Schnorr passthrough).
  - `lib.rs` — `pub const VESL_COIN_TYPE_PLACEHOLDER: u32 = 0x7E51_C0DE;` flagged as a placeholder pending upstream SLIP-44 registration. Override per-call via `from_seed_phrase`/`from_seed`.
  - 7 unit tests + 16 black-box integration tests in `tests/round_trip.rs` (BIP-39 vectors, role distinctness, account isolation, intent vs payment role-toggle round-trip, coin_type mismatch rejection, etc.).
- **Reserved a sixth Tip5 domain separator** in `vesl-signing`: `VESL_HD = "vesl-hd-v1"`. The HD transcript is segregated from every signing-side separator so a derivation transcript can never be confused for a signed message.
- **Public re-exports added to `vesl-signing::schnorr`**: `trunc_g_order` and `G_ORDER`, so HD callers can reduce arbitrary digest output into a valid scalar without re-vendoring the curve constants.

### Verified — `vesl-wallet`

- `cargo test --workspace --all-features --locked`: 78 tests pass (36 vesl-signing unit + 6 api-smoke + 1 parity stub + 7 vesl-wallet hd + 16 vesl-wallet integration + 3 vesl-wallet-spec + 2 doc-tests + 7 misc).
- `cargo clippy --workspace --all-targets --all-features -- -D warnings`: clean.
- `cargo fmt --all -- --check`: clean.
- `cargo deny check`: clean.

[`VESL_HD`]: https://docs.rs/vesl-signing/latest/vesl_signing/domain/domain_separators/constant.VESL_HD.html

### Added — Workspace scaffolding

- Workspace scaffolding: root `Cargo.toml`, three placeholder crates (`vesl-signing`, `vesl-wallet-spec`, `vesl-wallet`), CI pipeline (`cargo test`, `cargo clippy`, `cargo fmt`, `cargo deny`), `LICENSE-{MIT,APACHE}`, `README.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `deny.toml`, `rust-toolchain.toml` (pinned `stable`).

### Pending

- **`SchnorrSignatureJson` ownership** with x402-types maintainer (vesl-signing currently owns the canonical wire type; x402-types will need to re-export or maintain a structurally-identical type with `From` impls).
- **`nockchain-math::CheetahPoint` coordinate API** verification.
- **v0.1.0 tag**: mint after end-to-end verification across `vesl-wallet` / `vesl-core` / `vesl-nockup` / `x402-nockchain`.
- **v0.2.0**: `nockchain-math` parity-vector regen workflow; `SchnorrPrivateKey` zeroization (audit ref `vesl-core L-06`).

### Resolved

- **GitHub org confirmation** (2026-04-29): `zkvesl/vesl-wallet` (initially scaffolded as `zkvesl/vesl-identity`; renamed to `zkvesl/vesl-wallet` 2026-04-29 to match the headline crate). Matches existing convention with `zkvesl/x402-nockchain`, `zkvesl/vesl-core`, `zkvesl/hull-llm`.

## [0.0.0] — Scaffold

Initial workspace scaffold. No functional crates yet — `cargo build --workspace` and `cargo test --workspace` build green on three placeholder lib crates.

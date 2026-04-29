# vesl-identity

The Vesl identity stack: signing + wallet spec + ergonomic wallet API for the Nockchain ecosystem.

This is a workspace bundle. It ships three independently-`cargo add`-able crates that share a release cycle, test surface, and domain. The pattern follows `tokio` / `serde` / `clap`: one workspace repo, multiple crates published independently, consumers import what they need.

## Crates

| Crate | Status | Purpose |
|---|---|---|
| [`vesl-signing`](crates/vesl-signing) | scaffold (W1-3 lift in progress) | Schnorr-over-Cheetah signing, Tip5 domain separators, SIWN (CAIP-122). |
| [`vesl-wallet-spec`](crates/vesl-wallet-spec) | scaffold (W4-5) | BIP44 5-level layout convention. Doc-only. Closes OD#1 (`role=4` for x402 spending keys). |
| [`vesl-wallet`](crates/vesl-wallet) | scaffold (W6-8) | Ergonomic Hull-author wallet API. Pure-Rust HD derivation atop Cheetah. |

## Quick start (post-W3)

```toml
[dependencies]
vesl-signing = { git = "https://github.com/zkvesl/vesl-identity", tag = "v0.1.0" }
```

```rust
use vesl_signing::schnorr::{SchnorrPrivateKey, schnorr_sign};
use vesl_signing::prelude::Belt;

let mut belts = [Belt(0); 8];
belts[0] = Belt(42);
let key = SchnorrPrivateKey::from_belts(&belts)?;
let msg = [Belt(1), Belt(2), Belt(3), Belt(4), Belt(5)];
let (chal, sig) = schnorr_sign(&key, &msg)?;
```

## Math substrate

`vesl-signing` vendors its math primitives (Goldilocks `Belt`, Tip5 hash, Cheetah curve, F6 sextic extension). The crate has zero dependencies on the `nockchain-math` upstream or on `nockchain-tip5-rs`. Rationale (see `vesl-labs/docs/plans/shared-infrastructure/10-PHASE-0-NOW.md` and architectural decisions confirmed 2026-04-29):

- Self-contained = lean adoption surface for hardware-wallet vendors and external consumers (no nockchain-monorepo checkout required).
- Drift mitigation: a parity test suite compares vendored math byte-for-byte against `nockchain-math` HEAD on committed fixture vectors, regenerated quarterly.

## Development

```bash
cargo build --workspace
cargo test --workspace --all-features
cargo clippy --workspace --all-targets --all-features -- -D warnings
cargo fmt --all -- --check
cargo deny check
```

Toolchain pin: `stable` (see `rust-toolchain.toml`). MSRV: `1.85`.

## License

Dual-licensed under either of:

- Apache License, Version 2.0 ([LICENSE-APACHE](LICENSE-APACHE))
- MIT License ([LICENSE-MIT](LICENSE-MIT))

at your option.

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in this workspace by you, as defined in the Apache-2.0 license, shall be dual-licensed as above, without any additional terms or conditions.

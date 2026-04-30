# vesl-wallet

A Rust wallet library for Nockchain — Schnorr-over-Cheetah signing, BIP-44 layout convention, BIP-39 + custom Cheetah-BIP32-over-Tip5 HD derivation.

> **This is a library, not a wallet service.** `cargo add vesl-wallet` and run it in-process. There is no hosted backend, no remote signer, no online component. Mnemonics, keys, and signing all happen on the caller's machine.

This is a workspace bundle. It ships three independently-`cargo add`-able crates that share a release cycle, test surface, and domain. The pattern follows `tokio` / `serde` / `clap`: one workspace repo, multiple crates published independently, consumers import what they need.

## Crates

| Crate | Status | Purpose |
|---|---|---|
| [`vesl-signing`](crates/vesl-signing) | active | Schnorr-over-Cheetah signing, Tip5 domain separators, SIWN (CAIP-122). Foundation primitive — usable independently of the wallet (see below). |
| [`vesl-wallet-spec`](crates/vesl-wallet-spec) | active | BIP-44 5-level layout convention. Doc-only crate (constants + `DerivationPath` type). |
| [`vesl-wallet`](crates/vesl-wallet) | active | High-level wallet API. BIP-39 mnemonic + Cheetah-BIP32-over-Tip5 HD derivation + per-role signers. |

## Quick start

```toml
[dependencies]
vesl-wallet = { git = "https://github.com/zkvesl/vesl-wallet", tag = "v0.1.0" }
```

```rust
use vesl_wallet::{VeslWallet, VESL_COIN_TYPE_PLACEHOLDER};
use vesl_signing::prelude::Belt;

let wallet = VeslWallet::from_seed_phrase(
    "abandon abandon abandon abandon abandon abandon abandon abandon \
     abandon abandon abandon about",
    "",
    VESL_COIN_TYPE_PLACEHOLDER,
)?;

let msg = [Belt(1), Belt(2), Belt(3), Belt(4), Belt(5)];
let (chal, sig) = wallet.sign_intent(/* account = */ 0, &msg)?;
```

## Using `vesl-signing` without a wallet

The repo is named after its headline crate (`vesl-wallet`), but **`vesl-signing` is fully usable on its own** — it's the foundation primitive of the workspace, not a wallet implementation detail. If you're building any of the following, you want `vesl-signing` directly and can ignore the other two crates entirely:

- **Hardware-wallet firmware** that signs Cheetah transactions
- **Light-clients** that verify Schnorr-over-Cheetah signatures without holding keys
- **Oracle services / AVS task verifiers** that need signature aggregation
- **Trust-anchor signed statements** under the `vesl-authority-v1` domain separator
- **Anything else** that reaches for Schnorr-over-Cheetah without owning a wallet

```toml
[dependencies]
vesl-signing = { git = "https://github.com/zkvesl/vesl-wallet", tag = "v0.1.0" }
```

```rust
use vesl_signing::schnorr::{SchnorrPrivateKey, schnorr_sign};
use vesl_signing::prelude::Belt;
use ibig::UBig;

let key = SchnorrPrivateKey::new(UBig::from(42_424_242_u64))?;
let msg = [Belt(1), Belt(2), Belt(3), Belt(4), Belt(5)];
let (chal, sig) = schnorr_sign(&key, &msg)?;
```

## Math substrate

`vesl-signing` vendors its math primitives (Goldilocks `Belt`, Tip5 hash, Cheetah curve, F6 sextic extension). The crate has zero dependencies on the `nockchain-math` upstream or on `nockchain-tip5-rs`. Rationale:

- Self-contained = lean adoption surface for hardware-wallet vendors and external consumers (no nockchain-monorepo checkout required).
- Drift mitigation: a parity test suite compares vendored math byte-for-byte against `nockchain-math` HEAD on committed fixture vectors, regenerated periodically.

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

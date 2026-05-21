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

## Signing is not constant-time

> **Do not run vesl-signing's signing path in a hosted or multi-tenant
> setting.** `schnorr_sign`'s scalar multiplication (`ch_scal_big`) is
> not constant-time — its execution time depends on the secret nonce.
> An attacker who can measure signing timing can recover that nonce, and
> from the nonce plus the public signature, the private key.

For **local, self-custody signing** — a user signing their own
transactions on their own machine — this is not a realistic threat: an
attacker who can time the process can already read the key from memory.

For **hosted signing** — a signing service, co-located serverless, a
facilitator that signs for users, anything where a remote party submits
signing requests and measures responses — it is a real key-compromise
risk. A constant-time scalar multiplication is tracked as a prerequisite
for that deployment; until it lands, keep signing local.

## Replay protection is in-memory and per-process

`vesl-signing` ships `InMemoryReplayCache`, the stock `ReplayCache` impl. SIWN verification (`caip122::verify`) and any trust-anchor or AVS verifier built on `vesl-signing` use it to reject an already-seen signature.

The cache holds its seen-set in process memory. Two consequences for running a verifier as a service:

- **A restart empties it.** Nonces seen before a restart verify as fresh after one — the cache is a freshness window, not durable state.
- **A load-balanced fleet runs one cache per instance.** A nonce rejected by instance A is unknown to instance B; the same signed message submitted once to each instance is accepted by each.

No shared or persistent backend ships yet. Until one does, a multi-instance verifier must pin each client to a single instance with sticky sessions (load-balancer affinity) so its replay window stays consistent. Single-instance deployments are unaffected beyond the restart caveat. Where replay rejection has to survive a restart or span a fleet, back the cache with a uniqueness check at a durable layer.

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

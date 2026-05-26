# vesl-wallet

A Rust wallet library for Nockchain — Schnorr-over-Cheetah signing, BIP-44 layout, BIP-39 + Cheetah-BIP32-over-Tip5 HD derivation.

> **Library, not service.** `cargo add vesl-wallet` and run it in-process. No hosted backend, no remote signer. Mnemonics, keys, and signing happen on the caller's machine.

This is a workspace bundle that ships three independently-`cargo add`-able crates with a shared release cycle. Pattern follows `tokio` / `serde` / `clap`: one repo, multiple crates, consumers import what they need.

## Crates

| Crate | Purpose |
|---|---|
| [`vesl-signing`](crates/vesl-signing) | Schnorr-over-Cheetah signing, Tip5 domain separators, SIWN (CAIP-122). Foundation — usable independently of the wallet. |
| [`vesl-wallet-spec`](crates/vesl-wallet-spec) | BIP-44 5-level layout convention. Doc-only crate (constants + `DerivationPath` type). |
| [`vesl-wallet`](crates/vesl-wallet) | High-level wallet API. BIP-39 mnemonic + HD derivation + per-role signers. |

Most users want `vesl-wallet`. Hardware-wallet firmware, light-clients, or AVS verifiers that don't own keys want `vesl-signing` directly.

## Quick start — vesl-wallet

```toml
[dependencies]
vesl-wallet = { git = "https://github.com/zkvesl/vesl-wallet", tag = "v0.0.0" }
```

```rust
use vesl_wallet::{VeslWallet, VESL_COIN_TYPE_PLACEHOLDER};
use vesl_signing::prelude::Belt;

let wallet = VeslWallet::from_seed_phrase(
    "abandon abandon abandon abandon abandon abandon abandon abandon \
     abandon abandon abandon about",
    "",                    // optional BIP-39 passphrase
    VESL_COIN_TYPE_PLACEHOLDER,
)?;

let msg = [Belt(1), Belt(2), Belt(3), Belt(4), Belt(5)];
let (chal, sig) = wallet.sign_intent(/* account = */ 0, &msg)?;
```

## Quick start — vesl-signing standalone

Use cases where `vesl-signing` alone is the right dep:

- Hardware-wallet firmware that signs Cheetah transactions
- Light-clients that verify Schnorr-over-Cheetah signatures without holding keys
- Oracle services / AVS task verifiers that need signature aggregation
- Trust-anchor signed statements under the `vesl-authority-v1` domain separator

```toml
[dependencies]
vesl-signing = { git = "https://github.com/zkvesl/vesl-wallet", tag = "v0.0.0" }
```

```rust
use vesl_signing::schnorr::{SchnorrPrivateKey, schnorr_sign};
use vesl_signing::prelude::Belt;
use ibig::UBig;

let key = SchnorrPrivateKey::new(UBig::from(42_424_242_u64))?;
let msg = [Belt(1), Belt(2), Belt(3), Belt(4), Belt(5)];
let (chal, sig) = schnorr_sign(&key, &msg, /* domain = */ b"vesl-authority-v1")?;
```

## Constant-time disclaimer

**vesl-signing is not constant-time.** The Cheetah scalar multiplication uses variable-time field ops; an attacker who can time signing calls can reveal information about the secret scalar.

This is fine for **local use** — sign on the caller's machine, mnemonic stays under the user's control, no remote timing channel. It is NOT fine for **hosted signing** — exposing a remote API that signs on behalf of a user under a key the host knows is unsafe with the current implementation. A constant-time scalar multiplication is required for hosted signing; until one is implemented, keep signing local.

## Replay cache

`vesl-signing::replay::InMemoryReplayCache` rejects already-seen signatures by `(challenge, message_hash)`. SIWN verification (`caip122::verify`) and any trust-anchor or AVS verifier built on `vesl-signing` use `InMemoryReplayCache` to reject duplicates. The cache is in-memory and per-process — restart loses the seen-set. For multi-process or long-running verifiers, swap in a persistent backend implementing the `ReplayCache` trait.

## Math substrate

`vesl-signing` vendors `nockchain-math` and `nockchain-tip5-rs` into `crates/math/` for stable-toolchain consumers. The vendored copies track upstream releases via the pin file at `crates/math/PIN`. End-users get stable Rust, no nightly features, no upstream nockchain checkout.

## Development

```bash
cargo build --workspace
cargo test --workspace --all-features
cargo clippy --workspace --all-targets --all-features -- -D warnings
cargo fmt --all
cargo deny check
```

CI runs the same on every push.

## Documentation

- [zkvesl.org](https://zkvesl.org) — project home
- [docs.zkvesl.org](https://docs.zkvesl.org) — full guides
- [zkvesl/vesl-core](https://github.com/zkvesl/vesl-core) — protocol kernels + the SDK that consumes this signing primitive

## Maintainer

sobchek · <sobchek@zkvesl.org>

## License

Apache-2.0 OR MIT.

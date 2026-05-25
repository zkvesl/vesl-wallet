# Security Policy

## Reporting a Vulnerability

If you find a security issue in vesl-wallet — anything in the Schnorr
implementation, the BIP-39 / HD derivation tree, the CAIP-122 SIWN
flow, the Tip5 substrate, or anything that lets a signature verify
under conditions the spec says it shouldn't — please report it
privately via GitHub Security Advisories:

**[github.com/zkvesl/vesl-wallet/security/advisories/new](https://github.com/zkvesl/vesl-wallet/security/advisories/new)**

Do **not** open a public issue, post to chat, or otherwise disclose
the finding before a fix is shipped. We will coordinate disclosure
with you once a fix is ready.

## In scope

- Schnorr signing / verification (`vesl-signing/src/schnorr.rs`,
  `math/cheetah.rs`) — soundness, malleability, on-curve checks,
  scalar-range invariants
- Side-channel resistance (constant-time scalar multiplication, key
  zeroization, debug-format key residue)
- HD derivation (`vesl-wallet/src/hd.rs`) — non-hardened CKD properties,
  chain-code handling, key-confusion across roles
- BIP-39 mnemonic flow — seed phrase zeroization, parser strictness
- CAIP-122 / SIWN (`vesl-signing/src/caip122.rs`) — field-injection
  parser strictness, replay-cache binding, cross-chain / cross-resource
  separation, timestamp / window enforcement
- Tip5 boundary — anything that lets a Belt outside the Goldilocks
  field reach the hash function (cross-VM digest divergence)
- Domain-separator registry (`vesl-signing/src/domain.rs`) —
  reserved-vs-wired status of each tag, collision-resistance assertions

## Out of scope

- Bugs in upstream nockchain (report to `nockchain/nockchain` directly)
- The `sign_intent` API today behaves as a passthrough Schnorr signer
  pending upstream intent scripting; see its rustdoc and the
  `vesl-wallet-spec/SPEC.md §2 Role 0` placeholder note. Cross-domain
  signature reuse caveats are documented there, not security bugs.
- Style, documentation, or non-security correctness bugs — use the
  regular issue tracker

## Supported versions

The `dev` branch HEAD is the only supported surface today. After the
public beta tag lands, see the Releases page for the supported
version line.

## Acknowledgements

Security researchers who follow responsible disclosure are credited
by name in `CHANGELOG.md` and the corresponding GitHub Release notes,
unless they prefer anonymity.

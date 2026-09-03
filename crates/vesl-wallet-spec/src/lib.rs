//! Vesl wallet derivation spec — BIP44 5-level layout.
//!
//! Canonical role assignments and the typed [`DerivationPath`] holder used
//! by every Vesl-stack key derivation. The normative source is `SPEC.md`
//! at the crate root; this crate ships role-number constants and a typed
//! path holder so downstream crates and Hull authors refer to roles by
//! name rather than magic number.
//!
//! Key derivation lives in `vesl-wallet`. This crate intentionally has
//! no curve, no seed handling, no signing API.
//!
//! ## Path shape
//!
//! ```text
//! m / 44' / <coin_type>' / <agent_account>' / <role> / <index>
//! ```
//!
//! ## Roles
//!
//! - [`ROLE_INTENT`]    (`0`) — long-lived intent signing key
//! - [`ROLE_RECEIVING`] (`1`) — receiving / payout address
//! - [`ROLE_ENCRYPTION`](`2`) — encryption / delivery decryption (placeholder)
//! - [`ROLE_SESSION`]   (`3`) — short-lived delegation / session keys
//! - [`ROLE_X402`]      (`4`) — x402 spending keys
//! - [`ROLE_VOID`]      (`5`) — x402 hold-void (cancellation) keys
//!
//! Roles `6+` are reserved for future assignments — see `SPEC.md §5`.

#![forbid(unsafe_code)]
#![warn(missing_docs)]

/// BIP44 purpose value (constant per BIP44 spec).
pub const BIP44_PURPOSE: u32 = 44;

/// Role 0 — long-lived intent signing key (Schnorr-over-Cheetah).
///
/// Reserved for the `vesl_signing::domain::domain_separators::VESL_INTENT`
/// (`"vesl-intent-v1"`) Tip5 domain separator. Upstream intent scripting
/// has not landed yet, so the wallet's `sign_intent` accessor is currently
/// a raw passthrough — callers needing cross-protocol separation today
/// must hash under `VESL_INTENT` themselves. The role-0 path slot stays
/// stable so future binding lands without an HD-tree migration. See
/// `SPEC.md §2 Role 0` for the placeholder status and migration plan.
pub const ROLE_INTENT: u32 = 0;

/// Role 1 — receiving / payout address.
pub const ROLE_RECEIVING: u32 = 1;

/// Role 2 — encryption / delivery decryption.
///
/// Placeholder; the encryption primitive is pending the Vesl whitepaper.
/// Reserving the slot keeps the path stable across future encryption-scheme
/// choices.
pub const ROLE_ENCRYPTION: u32 = 2;

/// Role 3 — short-lived delegation / session keys.
///
/// Same Schnorr-over-Cheetah scheme as [`ROLE_INTENT`], derived at a
/// separate path so session-key compromise doesn't expose the role-0 master.
pub const ROLE_SESSION: u32 = 3;

/// Role 4 — x402 spending keys.
///
/// Signs under the `vesl_signing::domain::domain_separators::X402`
/// (`"x402-nockchain-v2"`) Tip5 domain separator.
pub const ROLE_X402: u32 = 4;

/// Role 5 — x402 **hold-void** keys: the dedicated, discardable key that
/// authorises cancelling one parked payment.
///
/// ⚑ *In plain terms: a throwaway key whose only job is to pre-authorise
/// giving one payment back. It signs once, immediately after the payment
/// lands, and is then useless.*
///
/// ⛔⛔ **IT MUST BE DERIVED AT THE SAME INDEX AS THE PAYMENT KEY IT
/// CANCELS, AND THAT IS A PRIVACY REQUIREMENT, NOT A CONVENIENCE.** A spend
/// publishes the signer's PUBKEY in its witness, so a void key that did not
/// rotate would be a permanent, public, on-chain identifier joining every job
/// that buyer ever paid for — an exposure the per-job secret it replaced
/// structurally did not have (x402 `PLAN_B §E1`, `§E3`).
///
/// ⛔ It is a **separate role** rather than another index under
/// [`ROLE_X402`] precisely so the two key spaces cannot collide: at one
/// role, "the void key for payment `i`" would have to be some other index
/// `j`, and `j` is a payment key for some other job.
///
/// ⛔⛔ **THE VOID KEY MUST NEVER EQUAL THE PAYMENT KEY.** The hold's void
/// branch and its capture branch are both 2-of-2 with the platform, and a
/// spend's signed digest covers its outputs and fee and **not the branch it
/// reveals** — so while the two branches named one buyer key, the buyer's
/// capture co-signature also spent the *void* branch, letting the platform be
/// paid while publishing no delivery key. A live node accepted exactly that,
/// twice, before the fix (x402 `records/S118`). Separate roles make the
/// collision unreachable by construction rather than refused by a check.
pub const ROLE_VOID: u32 = 5;

/// Typed BIP44 5-level derivation path.
///
/// Holds the four post-purpose components; the purpose is fixed at
/// [`BIP44_PURPOSE`]. No derivation logic lives here — see `vesl-wallet`
/// for HD key derivation.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct DerivationPath {
    /// SLIP-44 coin_type (TBD upstream — see `SPEC.md §4`).
    pub coin_type: u32,
    /// Per-agent account index.
    pub account: u32,
    /// One of the `ROLE_*` constants in this crate.
    pub role: u32,
    /// Rotation / sequence index within the role.
    pub index: u32,
}

impl DerivationPath {
    /// Construct a [`DerivationPath`] from its four post-purpose components.
    pub const fn new(coin_type: u32, account: u32, role: u32, index: u32) -> Self {
        Self {
            coin_type,
            account,
            role,
            index,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn role_constants_are_stable() {
        assert_eq!(BIP44_PURPOSE, 44);
        assert_eq!(ROLE_INTENT, 0);
        assert_eq!(ROLE_RECEIVING, 1);
        assert_eq!(ROLE_ENCRYPTION, 2);
        assert_eq!(ROLE_SESSION, 3);
        assert_eq!(ROLE_X402, 4);
        assert_eq!(ROLE_VOID, 5);
    }

    /// ⛔⛔ **THE ONE PROPERTY THE VOID KEY EXISTS FOR: AT EVERY INDEX IT IS
    /// A DIFFERENT PATH FROM THE PAYMENT KEY IT CANCELS.**
    ///
    /// ⚑ *In plain terms: the key that cancels a payment must never be the
    /// key that made it.* If the two coincided, the buyer's co-signature on
    /// the payout would also authorise the cancellation, and the platform
    /// could take the money without publishing the key that delivers the
    /// answer — measured accepted at consensus, twice, before the fix.
    ///
    /// ⛔ Asserted **over a range of indices, not at index 0**. A void key
    /// rotates with the payment key, so "they differ" has to hold at every
    /// index; checking one would pass for a `ROLE_VOID` that was accidentally
    /// defined as `ROLE_X402` with an offset.
    #[test]
    fn the_void_path_is_never_the_payment_path_at_any_index() {
        for index in [0u32, 1, 2, 7, 4096, u32::MAX] {
            let payment = DerivationPath::new(0, 0, ROLE_X402, index);
            let void = DerivationPath::new(0, 0, ROLE_VOID, index);
            assert_ne!(
                payment, void,
                "the void key must not be the payment key at index {index}"
            );
        }
    }

    #[test]
    fn derivation_path_eq_hash() {
        let p = DerivationPath::new(0, 0, ROLE_X402, 0);
        let q = DerivationPath {
            coin_type: 0,
            account: 0,
            role: 4,
            index: 0,
        };
        assert_eq!(p, q);

        // Hash equality follows from Eq + Hash derive contract; smoke-check
        // by inserting both into a HashSet and observing the dedupe.
        use std::collections::HashSet;
        let mut s: HashSet<DerivationPath> = HashSet::new();
        s.insert(p);
        s.insert(q);
        assert_eq!(s.len(), 1);
    }

    #[test]
    fn derivation_path_distinct_when_role_differs() {
        let intent = DerivationPath::new(0, 0, ROLE_INTENT, 0);
        let payment = DerivationPath::new(0, 0, ROLE_X402, 0);
        assert_ne!(intent, payment);
    }
}

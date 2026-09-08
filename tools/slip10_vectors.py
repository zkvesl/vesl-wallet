#!/usr/bin/env python3
"""Regenerate the SLIP-10 conformance vectors frozen in
`crates/vesl-wallet/tests/slip10_conformance.rs`.

This is a direct transcription of nockchain's OWN consensus implementation,
`nockchain/hoon/common/slip10.hoon`, arm by arm:

  +from-seed        :59-77    master derivation, with the invalid-key retry
  +derive-private   :140-181  child derivation, hardened and non-hardened
  ++domain-separator  :38     the 14 bytes `Nockchain seed`
  ++n               :36       g-order:curve, 255 bits (ztd/three.hoon:1496)

It exists so the frozen constants in the KAT are REGENERABLE rather than a
wall of unexplainable numbers: if upstream ever changes its derivation, run
this, watch it disagree, and the KAT tells you exactly which vector moved.

Scope, stated so the limit is not discovered later: everything here is pure
integer + HMAC work, so it covers the master key and every HARDENED step
with no elliptic-curve arithmetic at all.  The NON-HARDENED branch feeds the
parent PUBLIC KEY through `ser-a-pt` (slip10.hoon:155, ztd/three.hoon:1723)
and therefore needs Cheetah point arithmetic, which this script deliberately
does not reimplement -- that branch is pinned instead by the reference
wallet's own frozen vector, which is ground truth rather than a second
transcription of it.

Usage:  python3 tools/slip10_vectors.py
Exit 0 = the self-test reproduced the reference wallet's vectors.
"""

import hashlib
import hmac
import unicodedata

# ---------------------------------------------------------------------------
# Constants, each carrying the upstream line it is taken from.
# ---------------------------------------------------------------------------

# ++  n  g-order:curve  -- slip10.hoon:36 -> ztd/three.hoon:1496 ("255 bits")
G_ORDER = 0x7AF2599B3B3F22D0563FBF0F990A37B5327AA72330157722D443623EAED4ACCF

# ++  domain-separator  [14 'dees niahckcoN']  -- slip10.hoon:38.  The Hoon
# cord is byte-reversed; as a byte string it is the 14 bytes below.
DOMAIN_SEPARATOR = b"Nockchain seed"

# vesl_wallet::VESL_COIN_TYPE_PLACEHOLDER (crates/vesl-wallet/src/lib.rs:69)
VESL_COIN_TYPE_PLACEHOLDER = 0x7E51_C0DE
BIP44_PURPOSE = 44
ROLES = {
    "ROLE_INTENT": 0,
    "ROLE_RECEIVING": 1,
    "ROLE_ENCRYPTION": 2,
    "ROLE_SESSION": 3,
    "ROLE_X402": 4,
    # x402 hold-void (cancellation) keys -- vesl-wallet-spec ROLE_VOID.
    # NOTE: the role step is NON-HARDENED, so this script does not derive
    # role scalars at all (see the scope note above); the map is kept in step
    # with the spec crate so a reader is not told there are fewer roles than
    # there are.
    "ROLE_VOID": 5,
    # x402 withdrawal: where a swept spending pool lands. Same note applies.
    "ROLE_WITHDRAWAL": 6,
}

B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def b58decode(s: str) -> bytes:
    num = 0
    for ch in s:
        num = num * 58 + B58.index(ch)
    body = num.to_bytes((num.bit_length() + 7) // 8, "big")
    return b"\x00" * (len(s) - len(s.lstrip("1"))) + body


def hmac_sha512(key: bytes, data: bytes) -> bytes:
    return hmac.new(key, data, hashlib.sha512).digest()


def bip39_seed(mnemonic: str, passphrase: str = "") -> bytes:
    """BIP-39 mnemonic -> 64-byte seed.  The EMPTY passphrase is upstream's
    convention: `(to-seed:bip39 memo "")` -- apps/wallet/lib/s10.hoon:22."""
    m = unicodedata.normalize("NFKD", mnemonic)
    salt = unicodedata.normalize("NFKD", "mnemonic" + passphrase)
    return hashlib.pbkdf2_hmac("sha512", m.encode(), salt.encode(), 2048, 64)


# ---------------------------------------------------------------------------
# The derivation, transcribed.
# ---------------------------------------------------------------------------


def master_from_seed(seed: bytes):
    """+from-seed -- slip10.hoon:59-77.  Returns (scalar, chain_code, retries).

    NOTE one deliberate divergence: upstream tests only `?: (lth left n)`
    (:70), so it would ACCEPT a zero master key, while iris and the SLIP-10
    text both reject it (iris slip10.rs:95).  We follow iris and the spec.
    The two differ only on an event of probability 2^-256.
    """
    digest = hmac_sha512(DOMAIN_SEPARATOR, seed)
    retries = 0
    while True:
        left = int.from_bytes(digest[:32], "big")
        chain_code = digest[32:]
        if left < G_ORDER and left != 0:
            return left, chain_code, retries
        # +from-seed :72 -- re-hash the whole DERIVED digest under the separator
        digest = hmac_sha512(DOMAIN_SEPARATOR, digest)
        retries += 1


def derive_hardened(scalar: int, chain_code: bytes, index: int):
    """+derive-private, hardened branch -- slip10.hoon:140-181.

    `index` is the RAW index; the hardened bit is set here, and the retry
    at :176 re-uses the FULL (hardened) index, not the raw one.
    """
    if index >= 1 << 31:
        raise ValueError(f"index {index} already hardened")
    hardened = index | (1 << 31)
    # :153 -- [37 (can 3 ~[4^i 32^prv 1^0])]  ==  0x00 || ser256(prv) || ser32(i)
    data = b"\x00" + scalar.to_bytes(32, "big") + hardened.to_bytes(4, "big")
    digest = hmac_sha512(chain_code, data)
    retries = 0
    while True:
        left = int.from_bytes(digest[:32], "big")
        right = digest[32:]
        key = (left + scalar) % G_ORDER
        # :163 -- ?: &(!=(0 key) (lth left n))
        if left < G_ORDER and key != 0:
            return key, right, retries
        # :176 -- [37 (can 3 ~[4^i 32^right 1^0x1])], keyed on the PARENT cad
        digest = hmac_sha512(
            chain_code, b"\x01" + right + hardened.to_bytes(4, "big")
        )
        retries += 1


# ---------------------------------------------------------------------------
# Self-test against the reference wallet.
# ---------------------------------------------------------------------------

# Vectors produced by `nockchain-wallet keygen` / `derive-child --hardened 0`,
# reached via iris-rs/crates/iris-crypto/src/slip10.rs:121-162 which freezes
# that CLI output.  These are UPSTREAM ground truth, not a second guess at it.
REF_MNEMONIC = (
    "clutch inmate mango seek attract credit illegal popular term loyal "
    "fiber output trumpet lucky garbage merge menu certain dynamic aim "
    "trip fantasy master unveil"
)
REF_MASTER_PRV = "3MoHxVXWAr9qny12Sw8ZZtrgEBFcZegQQVkwYyePb9LZ"
REF_MASTER_CC = "3NhBRdy7vRw8vKQ5RnR3CNcD43WDn5Ky7mhhotqUcaiR"
REF_HARDENED_PRV = "CpMAmcgN1V6Majtx2HC7ULLXD9psA3Gg3nMye3JpKpH"
REF_HARDENED_CC = "8x7zh5LQA7tsFQQ3qsPfYGgFzQkoizGhLqLK7iKTGj3R"

# The mnemonic vesl-wallet's own tests use (tests/round_trip.rs:15).
CANONICAL_MNEMONIC = (
    "abandon abandon abandon abandon abandon abandon abandon abandon "
    "abandon abandon abandon about"
)


def self_test() -> bool:
    seed = bip39_seed(REF_MNEMONIC)
    prv, cc, retries = master_from_seed(seed)
    ok = True

    def check(label, got, want_b58, pad=32):
        nonlocal ok
        want = b58decode(want_b58).rjust(pad, b"\x00")
        good = got == want
        ok = ok and good
        print(f"  [{'ok' if good else 'FAIL'}] {label}")

    check("master private key", prv.to_bytes(32, "big"), REF_MASTER_PRV)
    check("master chain code", cc, REF_MASTER_CC)
    print(f"         master retries: {retries}")

    hprv, hcc, hretries = derive_hardened(prv, cc, 0)
    check("hardened child 0 key", hprv.to_bytes(32, "big"), REF_HARDENED_PRV)
    check("hardened child 0 chain code", hcc, REF_HARDENED_CC)
    print(f"         hardened retries: {hretries}  <- exercises slip10.hoon:176")
    return ok


def emit_prefix_vectors() -> None:
    """The hardened prefix m/44'/coin'/account' of vesl-wallet's five-role
    path (wallet.rs:112-116).  Levels 4 and 5 are non-hardened and are not
    computed here -- see the module docstring."""
    seed = bip39_seed(CANONICAL_MNEMONIC)
    scalar, cc, _ = master_from_seed(seed)
    print(f"  master           scalar={scalar:064x}")
    print(f"                   chain ={cc.hex()}")
    for label, idx in (
        ("44'", BIP44_PURPOSE),
        (f"coin' ({VESL_COIN_TYPE_PLACEHOLDER:#x})", VESL_COIN_TYPE_PLACEHOLDER),
        ("account' (0)", 0),
    ):
        scalar, cc, retries = derive_hardened(scalar, cc, idx)
        print(f"  {label:<28} scalar={scalar:064x}")
        print(f"  {'':<28} chain ={cc.hex()}   retries={retries}")


def main() -> int:
    p_retry = 1 - G_ORDER / (1 << 256)
    print("SLIP-10 over Cheetah -- vectors regenerated from nockchain's Hoon\n")
    print(f"curve order n     : {G_ORDER:#x}  ({G_ORDER.bit_length()} bits)")
    print(f"P(retry per step) : {p_retry:.4f}   E[HMAC calls/step]: "
          f"{(1 << 256) / G_ORDER:.4f}")
    print(f"P(5-level path takes no retry at all): "
          f"{(G_ORDER / (1 << 256)) ** 5:.4f}\n")

    print("self-test against `nockchain-wallet` output:")
    ok = self_test()

    print("\nvesl-wallet hardened prefix, CANONICAL_MNEMONIC:")
    emit_prefix_vectors()

    print("\n" + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

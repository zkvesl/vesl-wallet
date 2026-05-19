#!/usr/bin/env bash
# Validate that vesl-wallet stays pin-free.
#
# vesl-wallet ships as a pure local workspace with no upstream
# git-SHA dependencies — by design. It's pinned BY downstream
# (vesl-nockup bundles it, hull-llm doesn't depend on it directly),
# but it does not pin anything itself.
#
# This script enforces that invariant: a `rev = "<40-char-hex>"`
# entry creeping into any Cargo.toml is the kind of mistake that
# silently couples vesl-wallet's build to an upstream working tree
# and breaks the "standalone, tag-only" release contract.
#
# Exit 0 on clean. Exit 1 on any git-rev pin found.
#
# Usage: scripts/check-pins.sh
# Wired into ci.yml as a fast pre-flight gate.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

status=0

# Find every Cargo.toml in the repo (root + members + any nested).
# Exclude target/ build artifacts.
mapfile -t cargo_files < <(find . -name Cargo.toml -not -path './target/*' -not -path './*/target/*')

for f in "${cargo_files[@]}"; do
    # Match `rev = "<7-40 lowercase hex>"` — the shape Cargo accepts
    # for git-rev pins. Capture line numbers for clear diagnostics.
    hits=$(grep -nE 'rev[[:space:]]*=[[:space:]]*"[0-9a-f]{7,40}"' "$f" || true)
    if [[ -n "$hits" ]]; then
        echo "FAIL: $f carries git-rev pin(s):" >&2
        echo "$hits" | sed 's/^/  /' >&2
        status=1
    fi
done

# Also catch the `git = "..."` form even without a `rev = ...` on the
# same line — a tag/branch git-dep is also a no-go (mutable upstream
# coupling).
for f in "${cargo_files[@]}"; do
    hits=$(grep -nE 'git[[:space:]]*=[[:space:]]*"http' "$f" || true)
    if [[ -n "$hits" ]]; then
        echo "FAIL: $f carries git-source dep(s) (tag/branch/rev forbidden):" >&2
        echo "$hits" | sed 's/^/  /' >&2
        status=1
    fi
done

if [[ $status -eq 0 ]]; then
    echo "ok — vesl-wallet has no upstream git-SHA pins (checked ${#cargo_files[@]} Cargo.toml file(s))"
else
    echo "" >&2
    echo "vesl-wallet is meant to be standalone (no git-deps). Either:" >&2
    echo "  (a) remove the offending dependency, or" >&2
    echo "  (b) intentionally relax this invariant — edit scripts/check-pins.sh" >&2
fi

exit $status

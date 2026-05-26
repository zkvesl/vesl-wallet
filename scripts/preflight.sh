#!/usr/bin/env bash
# vesl-wallet push preflight — the local gate that defines "all clear to push."
#
# Runs the same checks ci.yml gates on. Any step's nonzero exit aborts
# the preflight.
#
# Manual run:
#   ./scripts/preflight.sh
#
# Pre-push hook:
#   scripts/hooks/pre-push invokes this for pushes targeting
#   refs/heads/{dev,main}. Opt in per-clone with:
#     git config core.hooksPath scripts/hooks
#
# Override (edge cases — known-flaky test, hotfix bypass, etc.):
#   git push --no-verify
#
# Speed: ~30–90s on a warm cargo cache; cargo-deny's first run downloads
# the advisory db and is slower.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

step() { printf '\n--- %s ---\n' "$1"; }

step "working tree"
if [[ -n "$(git status --porcelain)" ]]; then
    echo "preflight: uncommitted changes — commit or stash first" >&2
    git status --short >&2
    exit 1
fi
echo "clean."

step "branch"
branch=$(git rev-parse --abbrev-ref HEAD)
case "$branch" in
    dev|main) echo "$branch (ok)" ;;
    *)
        echo "preflight: on branch '$branch'; push gates run on dev/main only" >&2
        echo "  override: git push --no-verify" >&2
        exit 1
        ;;
esac

step "scripts/check-pins.sh"
./scripts/check-pins.sh

step "cargo fmt --all -- --check"
cargo fmt --all -- --check

step "cargo clippy --workspace --all-targets --all-features -- -D warnings"
cargo clippy --workspace --all-targets --all-features -- -D warnings

step "cargo test --workspace --all-features --locked"
cargo test --workspace --all-features --locked

step "cargo deny check"
cargo deny check

echo
echo "preflight: all clear."

#!/usr/bin/env bash
# release.sh — preflight + version bump + release-notes draft for a vesl-wallet tag.
#
# Usage: scripts/release.sh <version>
#   <version> — semver string, optionally with -beta.N / -rc.N prerelease. Leading 'v' stripped.
#
# Behavior:
#   1. Preflight: clean tree, on dev/local-dev, tests across feature gates,
#      clippy, cargo deny.
#   2. Bump [workspace.package].version and intra-workspace path-dep version pins
#      in crates/vesl-wallet/Cargo.toml (signing + wallet-spec).
#   3. Render release notes to /tmp/vesl-wallet-release-notes-<version>.md.
#   4. Commit the bump.
#
# Does NOT push. Does NOT tag. Tagging happens on origin/main after squash-push.

set -euo pipefail

VERSION=${1:?usage: scripts/release.sh <version>}
VERSION=${VERSION#v}

REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"

# --- Preflight ---
git diff --quiet || { echo "release.sh: uncommitted changes in working tree"; exit 1; }
git diff --cached --quiet || { echo "release.sh: staged but uncommitted changes"; exit 1; }

branch=$(git rev-parse --abbrev-ref HEAD)
[[ $branch == "dev" || $branch == "local-dev" ]] \
  || { echo "release.sh: must be on dev (or local-dev); current: $branch"; exit 1; }

echo "release.sh: running cargo test --workspace"
cargo test --workspace

echo "release.sh: running cargo test -p vesl-signing --no-default-features"
cargo test -p vesl-signing --no-default-features

echo "release.sh: running cargo clippy --workspace -- -D warnings"
cargo clippy --workspace -- -D warnings

if command -v cargo-deny >/dev/null 2>&1; then
  echo "release.sh: running cargo deny check"
  cargo deny check
else
  echo "release.sh: cargo-deny not installed; skipping (install: cargo install cargo-deny)"
  exit 1
fi

# --- Bump ---
OLD_VERSION=$(awk -F'"' '/^version *=/{print $2; exit}' Cargo.toml)
if [[ -z "$OLD_VERSION" ]]; then
  echo "release.sh: could not read current workspace version from Cargo.toml"
  exit 1
fi
echo "release.sh: bumping workspace version $OLD_VERSION -> $VERSION"

# Workspace version
sed -i "0,/^version = \"$OLD_VERSION\"/{s//version = \"$VERSION\"/}" Cargo.toml

# Intra-workspace path-dep version pins (appear alongside path= in
# crates/vesl-wallet/Cargo.toml; they don't enable crates.io fallback
# since we don't publish, but keeping them in sync with the workspace
# version avoids lockfile churn and signals current intent).
sed -i "s/version = \"$OLD_VERSION\"/version = \"$VERSION\"/g" crates/vesl-wallet/Cargo.toml

# --- Render notes ---
NOTES=/tmp/vesl-wallet-release-notes-${VERSION}.md
awk -v tag="$VERSION" -v ver="$VERSION" \
    '{
       gsub(/<TAG>/, tag);
       gsub(/<VERSION>/, ver);
       print
     }' scripts/release-notes.template.md > "$NOTES"

# --- Commit ---
git add Cargo.toml crates/vesl-wallet/Cargo.toml
git commit -m "release: vesl-wallet $VERSION"

echo
echo "release.sh: done."
echo "  notes:  $NOTES"
echo "  next:"
echo "    1. review $NOTES (fill in highlights / breaking / bug-fix sections)"
echo "    2. git push origin $branch"
echo "    3. squash-merge $branch into main on GitHub (or locally), then:"
echo "         git fetch origin main"
echo "         git tag -a v$VERSION -F $NOTES origin/main"
echo "         git push origin v$VERSION"
echo "    4. release.yml fires on the v$VERSION push and creates the GitHub Release"
echo "       using the tag annotation as the body."

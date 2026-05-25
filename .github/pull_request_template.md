<!--
Thanks for opening a PR! Quick checklist before you submit:

- [ ] PR targets `main`.
- [ ] `cargo test --workspace --all-features` passes locally.
- [ ] `cargo clippy --workspace --all-targets --all-features -- -D warnings` is clean.
- [ ] `cargo fmt --all -- --check` passes.
- [ ] `cargo deny check` passes (license + advisory gates).

If you touched `crates/vesl-signing/`, mention which primitive
changed in the summary so the reviewer can focus there — these
sit on every hull's signed-intent path.

First-time contributor? See CONTRIBUTING.md's "Good first PRs"
table — adding a test vector, runnable example, or rustdoc to a
public item is a template-shaped change that lands fast.
-->

## Summary

<!-- One or two sentences on what changed and why. -->

## Test plan

<!-- How did you verify the change? cargo test? a specific reference
     vector? round-trip against a Hull? Reference the relevant
     command + expected output. -->

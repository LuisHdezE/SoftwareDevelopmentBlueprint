# Blueprint 0.5.4-dev — Platform Capability Model

This hardening increment defines the project-level mobile capability contract for the future Blueprint 0.5.4 release while the root stable `VERSION` remains `0.5.3`.

## Contract

- `capabilities.android` and `capabilities.ios` are independent target declarations.
- `capabilities.ios` is optional in the schema so migrated 0.5.3 manifests may omit it; omission means iOS is not enabled.
- Every enabled mobile target requires a top-level `mobile.strategy` declaration.
- `mobile.strategy` accepts only `native` or `cross_platform`.
- `cross_platform` describes implementation/code sharing only. It does not enable Android or iOS automatically and does not merge platform gates, evidence, QA, review, or acceptance.
- `stack.mobile` remains a scalar technology declaration for compatibility. Strategy must not be embedded there.
- `offline_mobile: true` requires at least one mobile target and an `artifact_locations.openapi` path. This keeps 0.5.4 hardening inside the approved API-backed offline boundary.
- API-less/local-authoritative mobile remains deferred.

## Mobile Licensing compatibility

The 0.5.3 Android applicability boundary is preserved:

- Android enabled -> `capabilities.mobile_licensing` must be answered explicitly.
- iOS-only -> does not imply `mobile_licensing`.
- Android+iOS -> the Android target still triggers the existing explicit decision.
- `cross_platform` does not change licensing applicability.

This increment does not generalize the Mobile Licensing profile to iOS and does not change its 0.5.3 contract provenance.

## Scope boundary

This increment changes only project capability semantics. It does not yet add iOS to interface inventory namespaces, client architecture contracts, functional slices, evidence scopes, workflows, gates, or skills. Those remain separate governed increments.

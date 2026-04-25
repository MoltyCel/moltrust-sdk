# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] — 2026-04-25

### Added
- `MolTrustResolver` and `AsyncMolTrustResolver` classes for W3C DID resolution
  against `api.moltrust.ch`
- New types: `DIDDocument`, `ResolutionResult`, `ResolutionError`
- Native support for `did:moltrust:*` (including bridge-resolved `did:moltrust:ext_*`)
- `did:web:*` resolution support via the MolTrust API
- 19-test pytest suite covering unit + live integration cases
- `Typing :: Typed` classifier
- `[test]` extras: `pytest`, `pytest-asyncio`

### Changed
- `httpx` minimum version bumped from `>=0.25.0` to `>=0.27.0`
- README restructured with Python quickstart as the primary section
- `mcp_server.py` now reads `MOLTRUST_API_KEY` and `MOLTRUST_API_URL` from
  environment variables instead of hardcoded defaults
- `tests/test_integration.py` fallback for missing `MOLTRUST_API_KEY` is now
  empty string (was `***REMOVED***`)

### Notes
- `did:moltrust:ext_*` resolution depends on MolTrust API ≥ Phase-2 deploy
  (2026-04-25). Earlier API versions return HTTP 400 for bridged DIDs.
- `did:agentnexus:*` and `did:meeet:*` raise `ResolutionError("methodNotSupported")`.
  Bridge-resolution support is on the roadmap.

## [0.1.0] — 2026-02-19

### Added
- Initial release with `MolTrust` and `AsyncMolTrust` client classes
- `Agent`, `Credential`, `Reputation`, `VerificationResult` models
- `MolTrustError` exception
- Sync and async `register`, `verify`, `resolve`, `get_reputation`, `rate`,
  `issue_credential`, `verify_credential`, `did_document`, `health` methods

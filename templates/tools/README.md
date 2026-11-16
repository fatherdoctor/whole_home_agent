# Read tools

These Python standard-library tools keep credentials and registry contents out of CLI output.
Run them from the household repository root, or pass its root explicitly to the registry reader.

- `profile_check.py house/profile.yaml` validates the kit YAML subset and structural types. It does not
  establish readiness, rewrite the profile or accept unsupported YAML as a pass.
- `ha_read.py --fingerprint-url` prints a digest of the selected endpoint without reading a credential or
  connecting. The owner confirms the endpoint/context first; see `install/agent-access.md`.
- `ha_read.py --registry all` reads the three registries and prints counts. Its Python `RegistryReader` API
  returns rows in memory. The reader reuses `templates/export/export_house.py`; keep the kit folder layout.
  It never sends arbitrary commands or changes a Home Assistant registry.

Offline regressions:

```sh
python3 -m unittest discover -s templates/tools -p 'test_*.py'
python3 templates/tools/profile_check.py interview/profile-template.yaml
```

The transport's existing socket/frame regressions are in `templates/tests/test_export_existing.py`.
Tests use fake credentials and local fixtures; live behavior is not claimed from an offline pass.

## Target and credential details

The target record is SHA-256 of the normalized endpoint (scheme, host, nondefault port and path).
It prevents silent use of a different inherited URL. It does not attest physical identity through DNS,
a proxy or the shared Supervisor alias; inside an app the owner confirmation is the only identity check.
The runtime probe requests the unauthenticated API first, without redirects. The WebSocket reader checks
HTTP 101, Sec-WebSocket-Accept and auth_required before sending authentication. Transport failures return
fixed reason codes, never raw exception text. Only the three registry list commands are exposed by the CLI.

The private file is tried before HA_TOKEN and, on the internal route, SUPERVISOR_TOKEN. An explicitly selected
missing file or any unsafe existing file fails closed. The default file may be absent for environment-only
setups. The file must be named ha_token, outside the supplied household root, owned by the current user,
a regular file rather than a symlink or FIFO, and mode 0400 or 0600. Reads are bounded and nonblocking.
The export and first-look CLIs use this same reader and require the confirmed profile; use --root for the
household repository and --profile when its profile is elsewhere. Keep the kit templates/tools folder when
using scripts copied into house/export. Offline export diffs and first-look --offline do not load credentials.

The profile checker supports two-space mappings, block/flow lists and quoted/plain scalars. Anchors, tags,
block strings and multiple documents remain unverified. Shape validation never proves readiness.

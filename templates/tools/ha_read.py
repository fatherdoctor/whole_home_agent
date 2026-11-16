#!/usr/bin/env python3
"""Read only the area, device and entity registries; CLI output is counts, never registry contents.

Uses the kit's existing standard-library WebSocket transport in templates/export/export_house.py.
An owner-confirmed endpoint fingerprint is required before any credential is read or sent.
"""
import argparse
import hashlib
import hmac
import importlib.util
import json
import os
import pathlib
import re
import stat
import sys
import urllib.parse

SUPERVISOR_CORE = "http://supervisor/core"
REGISTRIES = {"areas": "config/area_registry/list", "devices": "config/device_registry/list",
              "entities": "config/entity_registry/list"}


class ReadError(ValueError):
    """Only fixed reason codes; never include a token, server error, URL or private filename."""


def normalized_url(value):
    try:
        if not isinstance(value, str) or any(c.isspace() or ord(c) < 32 for c in value):
            raise ValueError
        url = urllib.parse.urlsplit(value)
        if (url.scheme not in ("http", "https") or not url.hostname or url.username is not None
                or url.password is not None or url.query or url.fragment):
            raise ValueError
        host = url.hostname.encode("idna").decode("ascii").lower()
        host = "[" + host + "]" if ":" in host else host
        port = url.port
        authority = host + (":" + str(port) if port and port != (443 if url.scheme == "https" else 80) else "")
        path = url.path.rstrip("/")
        decoded = urllib.parse.unquote(path)
        if any(ord(c) < 32 or c.isspace() for c in decoded) or ".." in decoded.split("/"):
            raise ValueError
        return urllib.parse.urlunsplit((url.scheme, authority, path, "", ""))
    except (ValueError, UnicodeError):
        raise ReadError("invalid_endpoint") from None


def fingerprint_url(value):
    return hashlib.sha256(normalized_url(value).encode("utf-8")).hexdigest()


def require_target(value, profile):
    try:
        expected = profile["setup"]["agent_access"]["box_url_sha256"]
    except (KeyError, TypeError):
        raise ReadError("box_target_not_confirmed") from None
    if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
        raise ReadError("box_target_not_confirmed")
    base = normalized_url(value)
    if not hmac.compare_digest(fingerprint_url(base), expected):
        raise ReadError("box_target_mismatch")
    return base


def selected_url(env):
    value = env.get("HA_URL")
    if value:
        return value
    # Presence alone selects a route; do not read the credential before target verification.
    if any(key == "SUPERVISOR_TOKEN" for key in env):
        return SUPERVISOR_CORE
    raise ReadError("endpoint_unavailable")


def read_token(env, base, root, token_path=None):
    path = pathlib.Path(token_path or env.get("HA_TOKEN_FILE") or
                        pathlib.Path.home() / ".config/home-assistant/ha_token").expanduser()
    explicit = token_path is not None or bool(env.get("HA_TOKEN_FILE"))
    if not explicit and not path.exists() and not path.is_symlink():
        token = env.get("HA_TOKEN") or (env.get("SUPERVISOR_TOKEN") if base == SUPERVISOR_CORE else None)
        if not token:
            raise ReadError("credential_unavailable")
        if not isinstance(token, str) or any(c.isspace() for c in token):
            raise ReadError("invalid_credential_format")
        return token
    if path.name != "ha_token" or path.is_symlink():
        raise ReadError("unsafe_credential_file")
    try:
        if path.resolve().is_relative_to(pathlib.Path(root).resolve()):
            raise ReadError("credential_file_inside_repository")
        if not stat.S_ISREG(path.lstat().st_mode):
            raise ReadError("unsafe_credential_file")
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
        with os.fdopen(fd, "r", encoding="utf-8") as source:
            info = os.fstat(source.fileno())
            if (not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode) not in (0o400, 0o600)
                    or (hasattr(os, "getuid") and info.st_uid != os.getuid())):
                raise ReadError("unsafe_credential_permissions")
            token = source.read(8193).strip()
    except (OSError, UnicodeError):
        raise ReadError("credential_unavailable") from None
    if not token or len(token) > 8192 or any(c.isspace() for c in token):
        raise ReadError("invalid_credential_format")
    return token


def export_transport():
    path = pathlib.Path(__file__).resolve().parents[1] / "export/export_house.py"
    spec = importlib.util.spec_from_file_location("_kit_registry_transport", path)
    if spec is None or spec.loader is None:
        raise ReadError("transport_unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class RegistryReader:
    """Public request API accepts only the three registry names, never arbitrary WebSocket commands."""
    def __init__(self, profile, env=None, root=".", token_path=None, timeout=20, sock=None, transport=None):
        env = os.environ if env is None else env
        base = require_target(selected_url(env), profile)
        token = read_token(env, base, root, token_path)
        self.client = None
        try:
            module = transport or export_transport()
            self.client = module.WSClient.__new__(module.WSClient)
            module.WSClient.__init__(self.client, base, token, timeout=timeout, sock=sock)
            # The transport checks HTTP 101, Sec-WebSocket-Accept and HA's auth_required before sending auth.
        except (Exception, SystemExit):
            self.close()
            raise ReadError("connection_or_authentication_failed") from None

    def read(self, registry):
        if registry not in REGISTRIES:
            raise ReadError("unsupported_read")
        try:
            identifier = self.client.next_id
            self.client.next_id += 1
            self.client._send({"id": identifier, "type": REGISTRIES[registry]})
            for _ in range(1000):
                reply = self.client._recv()
                if reply.get("id") == identifier and reply.get("type") == "result":
                    if reply.get("success") is not True:
                        raise ReadError("registry_read_refused")
                    result = reply.get("result")
                    if not isinstance(result, list) or not all(isinstance(item, dict) for item in result):
                        raise ReadError("invalid_registry_response")
                    return result
            raise ReadError("registry_response_limit")
        except ReadError:
            raise
        except (Exception, SystemExit):
            raise ReadError("connection_or_authentication_failed") from None

    def close(self):
        sock = getattr(self.client, "sock", None)
        if sock is not None:
            try:
                sock.close()
            except OSError:
                pass

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


def profile_module():
    path = pathlib.Path(__file__).resolve().with_name("profile_check.py")
    spec = importlib.util.spec_from_file_location("_kit_read_profile", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def confirmed_access(root=".", profile_path="house/profile.yaml", env=None, url=None):
    env = os.environ if env is None else env
    root = pathlib.Path(root).resolve()
    path = pathlib.Path(profile_path)
    profile = profile_module().load_profile(path if path.is_absolute() else root / path)
    base = require_target(url or selected_url(env), profile)
    return base, read_token(env, base, root)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", default="house/profile.yaml")
    parser.add_argument("--root", default=".", help="household repository root, not a separate kit checkout")
    parser.add_argument("--registry", choices=(*REGISTRIES, "all"), default="all")
    parser.add_argument("--fingerprint-url", action="store_true",
                        help="locally fingerprint HA_URL without reading credentials or connecting")
    args = parser.parse_args(argv)
    try:
        if args.fingerprint_url:
            print(json.dumps({"box_url_sha256": fingerprint_url(selected_url(os.environ))}))
            return 0
        load_profile = profile_module().load_profile
        root = pathlib.Path(args.root).resolve()
        path = pathlib.Path(args.profile)
        profile = load_profile(path if path.is_absolute() else root / path)
        chosen = REGISTRIES if args.registry == "all" else (args.registry,)
        with RegistryReader(profile, root=root) as reader:
            counts = {name: len(reader.read(name)) for name in chosen}
        print(json.dumps({"status": "ok", "counts": counts}))
        return 0
    except ReadError as error:
        reason = str(error)
    except (Exception, SystemExit):
        reason = "profile_or_reader_unavailable"
    print(json.dumps({"status": "unverified", "reason": reason}))
    return 2


if __name__ == "__main__":
    sys.exit(main())

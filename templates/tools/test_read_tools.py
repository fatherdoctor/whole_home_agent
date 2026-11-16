"""Offline regressions for KIT-DRY.f3. No real credentials, endpoints or Home Assistant calls."""
import copy
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import subprocess
import types
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import ha_read as reader
import profile_check as profiles

spec = importlib.util.spec_from_file_location("runtime_under_test",
    os.environ.get("KIT_PROBE_UNDER_TEST", str(ROOT / "templates/runtime/probe_runtime.py")))
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
FAKE = "fixture" + "-credential"
URL = "http://" + "box.example.invalid"


def profile(url=URL):
    return {"setup": {"agent_access": {"box_url_sha256": reader.fingerprint_url(url)}}}


class RecordingEnv(dict):
    def get(self, key, default=None):
        if key in ("HA_TOKEN", "SUPERVISOR_TOKEN", "HA_TOKEN_FILE"):
            self.lookups.append(key)
        return super().get(key, default)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lookups = []


class TargetTests(unittest.TestCase):
    def test_url_normalization_and_fingerprint(self):
        self.assertEqual(reader.fingerprint_url(URL + ":80/"), reader.fingerprint_url(URL))
        self.assertNotEqual(reader.fingerprint_url(URL + ":8123"), reader.fingerprint_url(URL))

    def test_credentials_query_fragment_or_bad_scheme_rejected(self):
        for url in ("file:///fixture", URL + "?x=1", URL + "#x", "http://fixture:fixture@box.invalid",  # guard: allow synthetic invalid-URL fixture
                    URL + "/../other", URL + "/%0d%0a", URL + ":bad"):
            with self.subTest(url_kind=url.split(":")[0]), self.assertRaises(reader.ReadError):
                reader.normalized_url(url)

    def test_wrong_target_never_reads_credential_or_connects(self):
        env = RecordingEnv(HA_URL=URL, HA_TOKEN=FAKE)
        with patch.object(reader, "export_transport", side_effect=AssertionError("must not connect")):
            with self.assertRaisesRegex(reader.ReadError, "box_target_mismatch"):
                reader.RegistryReader(profile(URL + "/other"), env)
        self.assertEqual(env.lookups, [])

    def test_unconfirmed_target_never_reads_credential(self):
        env = RecordingEnv(HA_URL=URL, HA_TOKEN=FAKE)
        with self.assertRaisesRegex(reader.ReadError, "box_target_not_confirmed"):
            reader.RegistryReader({}, env)
        self.assertEqual(env.lookups, [])

    def test_supervisor_only_fingerprint_never_reads_credential(self):
        env, output = RecordingEnv(SUPERVISOR_TOKEN=FAKE), io.StringIO()
        with patch.object(reader.os, "environ", env), patch("sys.stdout", output):
            self.assertEqual(reader.main(["--fingerprint-url"]), 0)
        self.assertEqual(json.loads(output.getvalue()),
                         {"box_url_sha256": reader.fingerprint_url(reader.SUPERVISOR_CORE)})
        self.assertEqual(env.lookups, [])

    def test_private_file_permissions_and_outside_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            root.mkdir()
            private = Path(directory) / "ha_token"
            private.write_text(FAKE + "\n")
            private.chmod(0o600)
            self.assertEqual(reader.read_token({}, URL, root, private), FAKE)
            private.chmod(0o644)
            with self.assertRaisesRegex(reader.ReadError, "unsafe_credential_permissions"):
                reader.read_token({}, URL, root, private)
            inside = root / "ha_token"
            inside.write_text(FAKE)
            inside.chmod(0o600)
            with self.assertRaisesRegex(reader.ReadError, "credential_file_inside_repository"):
                reader.read_token({}, URL, root, inside)

    def test_unrelated_credential_filename_never_opened(self):
        with patch.object(Path, "open", side_effect=AssertionError("must not open")):
            with self.assertRaisesRegex(reader.ReadError, "unsafe_credential_file"):
                reader.read_token({}, URL, ROOT, Path("/tmp/other-credential-file"))

    def test_separate_household_repository_boundary(self):
        with tempfile.TemporaryDirectory() as directory:
            kit, house = Path(directory) / "kit", Path(directory) / "house-repo"
            kit.mkdir()
            house.mkdir()
            private = house / "private/ha_token"
            private.parent.mkdir()
            private.write_text(FAKE)
            private.chmod(0o600)
            target = house / "house/profile.yaml"
            target.parent.mkdir()
            text = (ROOT / "interview/profile-template.yaml").read_text()
            target.write_text(text.replace("    admin: false",
                '    box_url_sha256: "' + reader.fingerprint_url(URL) + '"\n    admin: false'))
            output, old_cwd = io.StringIO(), Path.cwd()
            try:
                os.chdir(house)
                with patch.dict(os.environ, {"HA_URL": URL, "HA_TOKEN_FILE": str(private)}, clear=True), \
                     patch.object(reader, "export_transport", side_effect=AssertionError("must not connect")), \
                     patch("sys.stdout", output):
                    self.assertEqual(reader.main([]), 2)
            finally:
                os.chdir(old_cwd)
            self.assertEqual(json.loads(output.getvalue())["reason"], "credential_file_inside_repository")

    @unittest.skipUnless(hasattr(os, "mkfifo"), "POSIX FIFO fixture")
    def test_fifo_rejected_without_waiting_for_a_writer(self):
        with tempfile.TemporaryDirectory() as directory:
            private = Path(directory) / "ha_token"
            os.mkfifo(private, 0o600)
            program = ("import sys; sys.path.insert(0, sys.argv[1]); import ha_read\n"
                       "try: ha_read.read_token({}, 'unused', sys.argv[3], sys.argv[2])\n"
                       "except ha_read.ReadError: print('blocked')\n")
            result = subprocess.run([sys.executable, "-c", program, str(HERE), str(private),
                                     str(Path(directory) / "repo")],
                                    capture_output=True, text=True, timeout=2)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout.strip(), "blocked")


class FakeSocket:
    closed = False

    def close(self):
        self.closed = True


class FakeClient:
    instances = []
    response = []
    failure = False

    def __init__(self, base, credential, timeout, sock):
        self.sock = sock or FakeSocket()
        self.next_id, self.sent = 1, []
        self.__class__.instances.append(self)
        if self.__class__.failure:
            raise ValueError(FAKE + " private endpoint")

    def _send(self, data):
        self.sent.append(data)

    def _recv(self):
        return {"id": self.next_id - 1, "type": "result", "success": True,
                "result": copy.deepcopy(self.__class__.response)}


class RegistryTests(unittest.TestCase):
    def setUp(self):
        FakeClient.instances, FakeClient.response, FakeClient.failure = [], [], False
        self.env = {"HA_URL": URL, "HA_TOKEN": FAKE}
        self.transport = types.SimpleNamespace(WSClient=FakeClient)

    def test_only_three_fixed_read_commands_and_increasing_ids(self):
        with reader.RegistryReader(profile(), self.env, transport=self.transport) as client:
            for kind in reader.REGISTRIES:
                self.assertEqual(client.read(kind), [])
        sent = FakeClient.instances[-1].sent
        self.assertEqual(sent, [{"id": i, "type": kind} for i, kind in
                               enumerate(reader.REGISTRIES.values(), 1)])
        self.assertTrue(FakeClient.instances[-1].sock.closed)

    def test_write_or_arbitrary_command_never_sent(self):
        with reader.RegistryReader(profile(), self.env, transport=self.transport) as client:
            for kind in ("call_service", "config/area_registry/create", "supervisor/api"):
                with self.assertRaisesRegex(reader.ReadError, "unsupported_read"):
                    client.read(kind)
        self.assertEqual(FakeClient.instances[-1].sent, [])

    def test_bad_response_is_not_a_registry(self):
        FakeClient.response = {"message": "fixture"}
        with reader.RegistryReader(profile(), self.env, transport=self.transport) as client:
            with self.assertRaisesRegex(reader.ReadError, "invalid_registry_response"):
                client.read("areas")

    def test_auth_failure_closes_socket_and_never_echoes_input(self):
        FakeClient.failure = True
        with self.assertRaisesRegex(reader.ReadError, "^connection_or_authentication_failed$"):
            reader.RegistryReader(profile(), self.env, transport=self.transport)
        self.assertTrue(FakeClient.instances[-1].sock.closed)

    def test_protocol_transport_is_the_shipped_stdlib_client(self):
        module = reader.export_transport()
        self.assertTrue(hasattr(module, "WSClient"))
        self.assertTrue(hasattr(module, "ws_frame"))


class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.text = (ROOT / "interview/profile-template.yaml").read_text()
        self.data = profiles.parse_profile(self.text)

    def test_real_template_valid_shape_not_readiness(self):
        self.assertIs(profiles.validate_profile(self.data), self.data)
        self.assertFalse(self.data["setup"]["done"])

    def test_block_and_flow_containers_quotes_and_comments(self):
        parsed = profiles.parse_profile("a:\n  - label: 'role''s label'\n    data: [one, 'two, three']\n"
                                        'b: {x: "a # b", y: null} # comment\n')
        self.assertEqual(parsed, {"a": [{"label": "role's label", "data": ["one", "two, three"]}],
                                  "b": {"x": "a # b", "y": None}})

    def test_duplicate_or_misindented_data_rejected(self):
        for text in ("a: 1\na: 2\n", "a:\n   b: 1\n", "a: 1\n  b: 2\n",
                     "a:\n  - label: null\n    label: other\n"):
            with self.subTest(case=len(text)), self.assertRaises(profiles.ProfileError):
                profiles.parse_profile(text)

    def test_unsupported_yaml_is_unverified(self):
        for text in ("a: &anchor x\n", "a: *anchor\n", "a: |\n  text\n",
                     "---\na: 1\n---\nb: 2\n", "a: !tag x\n"):
            with self.assertRaises(profiles.ProfileError) as caught:
                profiles.parse_profile(text)
            self.assertTrue(caught.exception.unsupported)

    def test_wrong_core_types_and_missing_sections_rejected(self):
        for path, value in ((("setup", "done"), "false"), (("profile", "topics"), []),
                            (("profile", "people"), ["role"]), (("setup", "budget", "buffer_pct"), 101)):
            data = copy.deepcopy(self.data)
            parent = data
            for key in path[:-1]:
                parent = parent[key]
            parent[path[-1]] = value
            with self.subTest(field=path[-1]), self.assertRaises(profiles.ProfileError):
                profiles.validate_profile(data)

    def test_nested_template_shapes_rejected(self):
        for path, value in ((("setup", "network", "router_control"), "false"),
                            (("profile", "notifications"), []),
                            (("profile", "agent", "unattended"), "true"),
                            (("profile", "devices", "integrations"), "fixture"),
                            (("adoption", "levels_passed"), [{"level": True, "on": "bad"}])):
            data, parent = copy.deepcopy(self.data), None
            parent = data
            for key in path[:-1]:
                parent = parent[key]
            parent[path[-1]] = value
            with self.subTest(field=path[-1]), self.assertRaises(profiles.ProfileError):
                profiles.validate_profile(data)

    def test_bad_single_quote_not_silently_accepted(self):
        with self.assertRaises(profiles.ProfileError):
            profiles.parse_profile("a: 'bad'quote'\n")

    def test_populated_adoption_on_keys_are_text(self):
        text = self.text.replace("levels_passed: []",
                                "levels_passed: [{level: 0, on: 2026-01-01}]")
        text = text.replace("once_done: []",
                            "once_done: [{check: L0-backup-proven, on: 2026-01-01}]")
        data = profiles.validate_profile(profiles.parse_profile(text))
        self.assertEqual(data["adoption"]["levels_passed"][0]["on"], "2026-01-01")
        self.assertEqual(data["adoption"]["once_done"][0]["on"], "2026-01-01")

    def test_credential_file_is_not_a_profile(self):
        with patch.object(Path, "open", side_effect=AssertionError("must not open")):
            with self.assertRaises(profiles.ProfileError):
                profiles.load_profile(Path("/tmp/ha_token"))


class ProbeTests(unittest.TestCase):
    def test_unbound_inherited_environment_rejected_before_request(self):
        env, calls = RecordingEnv(HA_URL=URL, HA_TOKEN=FAKE), []
        def fetch(url, headers):
            calls.append(headers)
            return (200, "[]") if url.endswith("/states") else (200, '{"message":"API running."}')
        self.assertEqual(runtime.probe_box(env, fetch)[0], "no")
        self.assertEqual(calls, [])
        self.assertEqual(env.lookups, [])

    def test_wrong_endpoint_rejected_before_request_or_credential(self):
        env = RecordingEnv(HA_URL=URL, HA_TOKEN=FAKE)
        with patch.object(runtime, "_fetch", side_effect=AssertionError("must not request")):
            self.assertEqual(runtime.probe_box(env, profile=profile(URL + "/other"))[0], "no")
        self.assertEqual(env.lookups, [])

    def test_pinned_endpoint_responds_before_credential_lookup(self):
        env, calls = RecordingEnv(HA_URL=URL, HA_TOKEN=FAKE), []
        def fetch(url, headers):
            if not calls:
                self.assertEqual(env.lookups, [])
                self.assertEqual(headers, {})
            calls.append(headers)
            if not headers:
                return 401, ""
            return (200, "[{},{}]") if url.endswith("/states") else (200, '{"message":"API running."}')
        self.assertEqual(runtime.probe_box(env, fetch, profile())[0], "yes")
        self.assertEqual(len(calls), 3)
        self.assertEqual(calls[0], {})

    def test_failed_preflight_never_reads_or_sends_credential(self):
        env = RecordingEnv(HA_URL=URL, HA_TOKEN=FAKE)
        self.assertEqual(runtime.probe_box(env, lambda *_: (302, ""), profile())[0], "no")
        self.assertEqual(env.lookups, [])

    def test_supervisor_preflight_uses_no_credential_before_binding(self):
        env, calls = RecordingEnv(SUPERVISOR_TOKEN=FAKE), []
        def fetch(url, headers):
            if not calls:
                self.assertEqual(env.lookups, [])
                self.assertEqual(headers, {})
            calls.append(headers)
            if not headers:
                return 401, ""
            return (200, "[]") if url.endswith("/states") else (200, '{"message":"API running."}')
        result = runtime.probe_box(env, fetch, profile(reader.SUPERVISOR_CORE))
        self.assertEqual(result, ("yes", "200, 0 entities, via the Supervisor (inside an add-on)"))
        self.assertEqual(len(calls), 3)

    def test_states_object_is_not_a_count(self):
        def fetch(url, headers):
            return (200, "{}") if url.endswith("/states") else (200, '{"message":"API running."}')
        self.assertEqual(runtime.probe_box({"HA_URL": URL, "HA_TOKEN": FAKE}, fetch, profile())[0], "no")

    def test_redirects_not_followed(self):
        self.assertIsNone(runtime.NoRedirect().redirect_request(None, None, None, None, None, None))


if __name__ == "__main__":
    unittest.main()

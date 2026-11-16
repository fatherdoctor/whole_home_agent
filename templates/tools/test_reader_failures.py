"""Real transport failure regressions; all sockets and credentials are synthetic."""
import base64
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ha_read as reader
from test_read_tools import URL, FAKE, profile, runtime


class Wire:
    def __init__(self, mode):
        self.mode, self.data, self.closed = mode, b'', False

    def sendall(self, data):
        transport = reader.export_transport()
        if data.startswith(b'GET '):
            key = next(line.split(b': ', 1)[1] for line in data.split(b'\r\n')
                       if line.startswith(b'Sec-WebSocket-Key:'))
            accept = base64.b64encode(hashlib.sha1(key + transport.WS_GUID.encode()).digest())
            self.data += b'HTTP/1.1 101 Switching Protocols\r\nSec-WebSocket-Accept: ' + accept + b'\r\n\r\n'
            self.data += transport.ws_frame(json.dumps({'type': 'wrong' if self.mode == 'greeting' else 'auth_required'}).encode(), mask=False)
            self.data += transport.ws_frame(json.dumps({'type': 'auth_invalid' if self.mode == 'auth' else 'auth_ok'}).encode(), mask=False)
        elif self.mode == 'oversize':
            self.data += b'\x81\x7f' + struct.pack('!Q', transport.WS_MAX_FRAME + 1)

    def recv(self, count):
        data, self.data = self.data[:count], self.data[count:]
        return data

    def close(self):
        self.closed = True


class FailureTests(unittest.TestCase):
    def test_real_transport_failures_become_fixed_json(self):
        for mode in ('auth', 'greeting', 'closed', 'oversize', 'unreachable'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / 'profile.yaml'
                path.write_text('setup:\n  agent_access:\n    box_url_sha256: "' + reader.fingerprint_url(URL) + '"\n')
                # The CLI profile loader validates the full profile in normal use. Here only transport is under test.
                wire, output = Wire(mode), io.StringIO()
                original = reader.RegistryReader
                def build(data, **kwargs):
                    return original(data, env={'HA_URL': URL, 'HA_TOKEN': FAKE}, sock=None if mode == 'unreachable' else wire)
                with patch.object(reader, 'load_profile', return_value=profile(), create=True), \
                     patch.object(reader, 'RegistryReader', side_effect=build), \
                     patch('socket.create_connection', side_effect=OSError('private endpoint detail')), \
                     contextlib.redirect_stdout(output):
                    # Patch the path-loaded module loader rather than bypassing the real WebSocket client.
                    if hasattr(reader, 'profile_module'):
                        module = reader.profile_module()
                        with patch.object(reader, 'profile_module', return_value=module), patch.object(module, 'load_profile', return_value=profile()):
                            rc = reader.main(['--profile', str(path), '--root', directory])
                    else:
                        import profile_check
                        with patch.object(profile_check, 'load_profile', return_value=profile()):
                            rc = reader.main(['--profile', str(path), '--root', directory])
                self.assertEqual(rc, 2)
                self.assertEqual(json.loads(output.getvalue()), {'status': 'unverified', 'reason': 'connection_or_authentication_failed'})
                if mode != 'unreachable':
                    self.assertTrue(wire.closed)

    def test_isolated_cli_loads_profile_by_path(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'profile.yaml'
            path.write_text((Path(__file__).resolve().parents[2] / 'interview/profile-template.yaml').read_text())
            env = {key: value for key, value in os.environ.items() if key not in ('HA_URL', 'HA_TOKEN', 'SUPERVISOR_TOKEN')}
            result = subprocess.run([sys.executable, '-I', str(Path(reader.__file__)), '--profile', str(path)], env=env, capture_output=True, text=True)
            self.assertEqual(json.loads(result.stdout)['reason'], 'endpoint_unavailable')

    def test_missing_profile_is_unknown_and_plain(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(runtime.probe_box({}, root=directory), ('unknown', 'no house/profile.yaml yet; confirm the box in install/agent-access.md section 2'))

    def test_file_precedes_environment_and_bad_file_never_falls_back(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'ha_token'
            path.write_text(FAKE)
            path.chmod(0o600)
            env = {'HA_TOKEN': 'stale', 'HA_TOKEN_FILE': str(path)}
            self.assertEqual(reader.read_token(env, URL, Path(directory) / 'repo'), FAKE)
            path.chmod(0o644)
            with self.assertRaisesRegex(reader.ReadError, 'unsafe_credential_permissions'):
                reader.read_token(env, URL, Path(directory) / 'repo')

    def test_export_and_first_look_use_confirmed_file_first_access(self):
        import importlib.util
        root = Path(__file__).resolve().parents[2]
        spec = importlib.util.spec_from_file_location('export_access_test', root / 'templates/export/export_house.py')
        export = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(export)
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / 'repo'
            (repo / 'house').mkdir(parents=True)
            token_path = Path(directory) / 'ha_token'
            token_path.write_text(FAKE)
            token_path.chmod(0o600)
            text = (root / 'interview/profile-template.yaml').read_text()
            text = text.replace('    admin: false', '    box_url_sha256: "' + reader.fingerprint_url(URL) + '"\n    admin: false')
            (repo / 'house/profile.yaml').write_text(text)
            with patch.dict(os.environ, {'HA_URL': URL, 'HA_TOKEN': 'stale', 'HA_TOKEN_FILE': str(token_path)}, clear=True):
                self.assertEqual(export.confirmed_access(repo), (URL, FAKE))
                with patch.object(export, 'http_fetch', side_effect=AssertionError('must not connect')):
                    with patch.dict(os.environ, {'HA_URL': URL + '/wrong'}):
                        with self.assertRaises(SystemExit) as caught:
                            export.main(['--root', str(repo), '--basic'])
                self.assertNotIn(URL, str(caught.exception))
                self.assertNotIn(FAKE, str(caught.exception))
            spec = importlib.util.spec_from_file_location('first_access_test', root / 'templates/export/first_look.py')
            first = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(first)
            with patch.object(first, 'load_export', return_value={'automations.json': [], 'entities.json': []}), \
                 patch.object(first, 'gather_live', return_value={}) as gather, \
                 patch.object(first, 'context', return_value={}), patch.object(first, 'run_checks', return_value=[]), \
                 patch.object(first, 'render_first_look', return_value='offline test'), \
                 patch.dict(os.environ, {'HA_URL': URL, 'HA_TOKEN': 'stale', 'HA_TOKEN_FILE': str(token_path)}, clear=True), \
                 contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(first.main(['--root', str(repo), '--profile', str(repo / 'house/profile.yaml'), '--out', str(repo / 'out')]), 0)
                self.assertEqual(gather.call_args.args[1:3], (URL, FAKE))

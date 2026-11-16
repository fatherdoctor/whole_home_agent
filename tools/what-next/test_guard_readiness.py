"""Offline regressions for KIT-DRY.f8; no remote is contacted."""
import ast
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(os.environ.get('WHAT_NEXT_UNDER_TEST', Path(__file__).with_name('what_next.py')))
spec = importlib.util.spec_from_file_location('wn', SOURCE)
wn = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wn)


class GuardReadiness(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        subprocess.run(['git', '-C', str(self.root), 'remote', 'add', 'origin', 'fixture-remote'], check=True)
        (self.root/'guard').mkdir()
        for name in ('selftest.py', 'push_guard.py', 'names.example.txt'):
            shutil.copy(ROOT/'templates/guard'/name, self.root/'guard'/name)
        self.hook = self.root/'.git/hooks/pre-push'
        self.hook.write_text('#!/bin/sh\nexec python3 guard/push_guard.py --repo . --remote "$1" --pushed-refs\n')
        self.hook.chmod(0o644)

    def check(self, selftest=True):
        return next(c for c in wn.level1(self.root, None, 'missing', False, selftest, None) if c['id']=='L1-guard')

    def manual(self):
        p=self.root/'house/docs/CHANGELOG.md'
        p.parent.mkdir(parents=True)
        p.write_text('L1-guard: method=manual; reason=diagnosed runtime restriction\n')

    def fake(self, hook, rc=0, planted=0):
        original=wn.run
        def run(cmd, root, **kwargs):
            if 'guard/selftest.py' in cmd:
                if '--check-hook' in cmd:
                    return subprocess.CompletedProcess(cmd,rc,json.dumps(hook),'')
                return subprocess.CompletedProcess(cmd,planted,'fixture output','')
            return original(cmd,root,**kwargs)
        return patch.object(wn,'run',side_effect=run)

    def test_nonexecutable_hook_fails(self):
        self.assertEqual(self.check()['result'],'fail')

    def test_no_selftest_is_unknown(self):
        self.assertEqual(self.check(False)['result'],'unknown')

    def test_record_does_not_bypass_broken_installation(self):
        self.manual()
        self.assertEqual(self.check()['result'],'fail')

    def test_manual_is_named_manual_never_pass(self):
        self.manual()
        with self.fake({'status':'unavailable','method':'unverified','reason':'hook_execution_denied'},2):
            c=self.check()
        self.assertEqual((c['result'],c['method']),('manual','manual'))

    def test_execution_denial_without_record_is_unknown(self):
        with self.fake({'status':'unavailable','method':'unverified','reason':'hook_execution_denied'},2):
            self.assertEqual(self.check()['result'],'unknown')

    def test_hook_needs_planted_checks(self):
        with self.fake({'status':'pass','method':'hook','reason':'hook_exit_0'},planted=1):
            self.assertEqual(self.check()['result'],'fail')

    def test_both_checks_prove_hook(self):
        with self.fake({'status':'pass','method':'hook','reason':'hook_exit_0'}):
            c=self.check()
        self.assertEqual((c['result'],c['method']),('pass','hook'))

    def test_old_checker_exit_zero_without_json_is_unknown(self):
        original=wn.run
        def run(cmd,root,**kwargs):
            if 'guard/selftest.py' in cmd:return subprocess.CompletedProcess(cmd,0,'all pass','')
            return original(cmd,root,**kwargs)
        with patch.object(wn,'run',side_effect=run):
            self.assertEqual(self.check()['result'],'unknown')

    def test_manual_record_never_bypasses_refusal(self):
        self.manual()
        with self.fake({'status':'fail','method':'hook','reason':'hook_refused'},1):
            self.assertEqual(self.check()['result'],'fail')

    def test_checker_output_is_not_echoed(self):
        with self.fake({'private':'fixture-sensitive-output'},3):
            self.assertNotIn('fixture-sensitive-output',self.check()['evidence'])

    def test_install_recipe_leaves_names_check_explicitly_off(self):
        self.hook.unlink()
        recipe=Path(os.environ.get('GUARD_README_UNDER_TEST', ROOT/'templates/guard/README.md')).read_text().split('```sh',1)[1].split('```',1)[0]
        recipe=recipe.replace('<kit>',str(ROOT))
        subprocess.run(['sh','-c',recipe],cwd=self.root,check=True,capture_output=True,text=True)
        self.assertFalse((self.root/'guard/names.txt').exists())
        # The guard's explicit missing-list notice is part of the first-push contract.
        subprocess.run(['git','-C',str(self.root),'add','.gitignore'],check=True)
        subprocess.run(['git','-C',str(self.root),'-c','user.name=fixture','-c','user.email=fixture@example.invalid',
                        'commit','-qm','fixture'],check=True)
        result=subprocess.run([sys.executable,str(self.root/'guard/push_guard.py'),'--repo',str(self.root),
                               '--range','HEAD..HEAD'],capture_output=True,text=True,check=True)
        self.assertIn('household-names check is off',result.stderr)

    def test_restricted_runtime_counts_skips_and_keeps_exit_one(self):
        script="""import errno,runpy,subprocess,sys
original=subprocess.Popen
def restricted(args,*a,**kw):
    if args[0] not in ('git',sys.executable):
        raise PermissionError(errno.EACCES,'fixture execution restriction')
    return original(args,*a,**kw)
subprocess.Popen=restricted
sys.argv=[sys.argv[1]]
runpy.run_path(sys.argv[0],run_name='__main__')
"""
        r=subprocess.run([sys.executable,'-c',script,str(Path(os.environ.get('GUARD_SELFTEST_UNDER_TEST', ROOT/'templates/guard/selftest.py')))],
                         capture_output=True,text=True,timeout=90)
        self.assertEqual(r.returncode,1)
        self.assertIn('this computer or sandbox ('+sys.platform+') will not run hook files',r.stdout)
        self.assertIn('SKIP hook check:',r.stdout)
        self.assertNotIn('FAIL hook check:',r.stdout)
        self.assertIn('0 failing;',r.stdout)

    def test_manual_changelog_bullet_and_bold_forms(self):
        p=self.root/'house/docs/CHANGELOG.md'
        p.parent.mkdir(parents=True)
        for prefix,suffix in [('- ',''),('- **','**'),('  - **','**'),('    ','')]:
            with self.subTest(prefix=prefix):
                p.write_text(prefix+'L1-guard: method=manual; reason=diagnosed restriction'+suffix+'\n')
                with self.fake({'status':'unavailable','method':'unverified','reason':'hook_execution_denied'},2):
                    c=self.check()
                self.assertEqual((c['result'],c['method']),('manual','manual'))

    def test_known_checker_reason_is_retained(self):
        self.assertIn('hook_execute_bits_missing',self.check()['evidence'])
        with self.fake({'status':'error','method':'unverified','reason':'hook_wiring_unverified'},3):
            self.assertIn('hook_wiring_unverified',self.check()['evidence'])

    def test_unknown_checker_reason_is_not_echoed(self):
        with self.fake({'status':'error','method':'unverified','reason':'fixture-sensitive-output'},3):
            self.assertNotIn('fixture-sensitive-output',self.check()['evidence'])

    def test_native_skip_probe_requires_exact_execution_denied(self):
        source=(ROOT/'templates/tests/test_templates.py').read_text()
        tree=ast.parse(source)
        definition=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='hook_execution_denied')
        namespace={'json':json,'subprocess':subprocess,'sys':sys}
        exec(compile(ast.Module(body=[definition],type_ignores=[]),'<native hook probe>','exec'),namespace)
        probe=namespace['hook_execution_denied']
        for rc,data,want in [
            (2,{'status':'unavailable','method':'unverified','reason':'hook_execution_denied'},True),
            (3,{'status':'error','method':'unverified','reason':'hook_execute_bits_missing'},False),
            (0,{'status':'pass','method':'hook','reason':'hook_exit_0'},False),
            (0,{'status':'unavailable','method':'unverified','reason':'hook_execution_denied'},False),
        ]:
            with patch.object(subprocess,'run',return_value=subprocess.CompletedProcess([],rc,json.dumps(data),'')):
                self.assertEqual(probe(self.root),want)


if __name__=='__main__':unittest.main()

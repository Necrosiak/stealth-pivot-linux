"""Run install/uninstall in a temporary filesystem, never the host's /etc."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class InstallationTests(unittest.TestCase):
    def test_install_repeat_and_restore_previous_configuration(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            repo = base / 'repo'
            repo.mkdir()
            shutil.copytree(ROOT / 'files', repo / 'files')
            fake_root = base / 'root'
            for path in ['run/systemd/system', 'etc/systemd/system', 'etc/udev/rules.d']:
                (fake_root / path).mkdir(parents=True, exist_ok=True)
            previous = fake_root / 'etc/udev/rules.d/71-nm-stealth-pivot-xpad.rules'
            previous.write_text('# previous workaround\n')
            unrelated = fake_root / 'etc/udev/rules.d/unrelated.rules'
            unrelated.write_text('# keep me\n')
            bin_dir = base / 'bin'
            bin_dir.mkdir()
            for name in ['systemctl', 'udevadm', 'modprobe', 'modinfo']:
                stub = bin_dir / name
                stub.write_text('#!/bin/sh\nexit 0\n')
                stub.chmod(0o755)
            for name in ['install.sh', 'uninstall.sh']:
                script = (ROOT / name).read_text()
                script = script.replace('[[ $EUID == 0 ]]', '[[ 1 == 1 ]]')
                for prefix in ['/etc/', '/var/', '/run/']:
                    script = script.replace(prefix, str(fake_root) + prefix)
                (repo / name).write_text(script)
            # Hardware detection is tested separately; do not read the host from this test.
            (repo / 'status.sh').write_text('#!/bin/sh\nexit 0\n')
            (repo / 'status.sh').chmod(0o755)
            env = dict(os.environ, PATH=str(bin_dir) + ':' + os.environ['PATH'])
            def run(name):
                result = subprocess.run(['bash', str(repo / name)], env=env, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
            run('install.sh')
            self.assertIn('SYSTEMD_WANTS', previous.read_text())
            run('install.sh')
            backup = fake_root / 'var/lib/stealth-pivot-linux/original/71-nm-stealth-pivot-xpad.rules'
            self.assertEqual(backup.read_text(), '# previous workaround\n')
            run('uninstall.sh')
            self.assertEqual(previous.read_text(), '# previous workaround\n')
            self.assertEqual(unrelated.read_text(), '# keep me\n')
            self.assertFalse((fake_root / 'etc/stealth-pivot/bind-xpad').exists())
            self.assertFalse((fake_root / 'etc/systemd/system/nm-stealth-pivot-xpad.service').exists())
            run('uninstall.sh')

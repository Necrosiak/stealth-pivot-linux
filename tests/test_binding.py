"""Exercise the actual helper with a temporary sysfs tree and stub modprobe."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class BindingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.usb = self.base / 'sys/bus/usb'
        (self.usb / 'devices').mkdir(parents=True)
        (self.usb / 'drivers/xpad').mkdir(parents=True)
        self.ids = self.usb / 'drivers/xpad/new_id'
        self.ids.write_text('')
        self.probe = self.usb / 'drivers_probe'
        self.probe.write_text('')
        self.bin = self.base / 'bin'
        self.bin.mkdir()
        modprobe = self.bin / 'modprobe'
        modprobe.write_text('#!/bin/sh\nexit "${MODPROBE_RESULT:-0}"\n')
        modprobe.chmod(0o755)
        source = (ROOT / 'files/bind-xpad').read_text()
        source = source.replace('/sys/bus/usb', str(self.usb))
        source = source.replace('/run/lock/nm-stealth-pivot-xpad.lock', str(self.base / 'lock'))
        self.helper = self.base / 'helper'
        self.helper.write_text(source)

    def device(self, name='1-2', vid='10f5', pid='7101', cls='ff', sub='5d', proto='01', driver=None):
        parent = self.usb / 'devices' / name
        parent.mkdir(exist_ok=True)
        (parent / 'idVendor').write_text(vid)
        (parent / 'idProduct').write_text(pid)
        iface = self.usb / 'devices' / (name + ':1.0')
        iface.mkdir()
        for key, value in [('bInterfaceClass', cls), ('bInterfaceSubClass', sub), ('bInterfaceProtocol', proto)]:
            (iface / key).write_text(value)
        if driver:
            (iface / 'driver').symlink_to(self.usb / 'drivers' / driver)
        return iface.name

    def run_helper(self, **extra):
        env = dict(os.environ, PATH=str(self.bin) + ':' + os.environ['PATH'], **extra)
        return subprocess.run(['bash', str(self.helper)], env=env, capture_output=True, text=True)

    def test_registers_and_probes_receiver(self):
        iface = self.device()
        result = self.run_helper()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.ids.read_text(), '10f5 7101 ff\n')
        self.assertEqual(self.probe.read_text(), iface)

    def test_already_registered_does_not_overwrite_ids(self):
        self.ids.write_text('1234 5678 ff\n10f5 7101 ff\n')
        self.device()
        self.assertEqual(self.run_helper().returncode, 0)
        self.assertEqual(self.ids.read_text(), '1234 5678 ff\n10f5 7101 ff\n')

    def test_existing_native_binding_is_left_alone(self):
        self.device(driver='xpad')
        self.assertEqual(self.run_helper().returncode, 0)
        self.assertEqual(self.ids.read_text(), '')
        self.assertEqual(self.probe.read_text(), '')

    def test_hid_interface_is_not_probed(self):
        self.device(cls='03', sub='00', proto='00')
        self.assertEqual(self.run_helper().returncode, 0)
        self.assertEqual(self.probe.read_text(), '')

    def test_other_receiver_is_not_probed(self):
        self.device(pid='7005')
        self.assertEqual(self.run_helper().returncode, 0)
        self.assertEqual(self.probe.read_text(), '')

    def test_no_receiver_is_valid_at_boot(self):
        self.assertEqual(self.run_helper().returncode, 0)
        self.assertEqual(self.ids.read_text(), '10f5 7101 ff\n')
        self.assertEqual(self.probe.read_text(), '')

    def test_missing_module_fails_without_registration(self):
        self.assertNotEqual(self.run_helper(MODPROBE_RESULT='1').returncode, 0)
        self.assertEqual(self.ids.read_text(), '')

    def test_missing_new_id_fails(self):
        self.ids.unlink()
        (self.usb / 'drivers/xpad').rmdir()
        self.assertNotEqual(self.run_helper().returncode, 0)

# Turtle Beach Stealth Pivot on Linux

Make the **Stealth Pivot 2.4 GHz USB receiver (`10f5:7101`)** discoverable by Linux's existing `xpad` driver and Steam Input.

This is a small persistent compatibility workaround, not an official Turtle Beach driver or a replacement kernel module. No DKMS, kernel compilation or firmware download is needed.

[Documentation française](README.fr.md)

## Install

Requires Linux with **systemd, udev and the kernel's `xpad` module**, plus Bash, kmod and util-linux (`flock`). Install Git using your distribution if needed.

```bash
git clone https://github.com/Necrosiak/stealth-pivot-linux.git
cd stealth-pivot-linux
sudo bash install.sh
```

Turn on the controller and pair it with its receiver. Steam may show **Generic X-Box pad**. You can then use Steam's controller input test.

```bash
bash status.sh
```

A successful registration service normally shows `inactive (dead)`: it performs its work and exits. `enabled` means it will run at the next boot.

### Update this workaround

```bash
cd stealth-pivot-linux
git pull --ff-only
sudo bash install.sh
```

No automatic updater is installed.

### Uninstall

```bash
sudo bash uninstall.sh
```

This restores files that existed before the first installation, including an earlier local workaround. Backups remain in `/var/lib/stealth-pivot-linux/original`. It does not disconnect a working controller; reboot to clear the dynamic driver registration. If a previous workaround was restored, that workaround can register the receiver again.

## How it works

The receiver exposes a vendor-specific gamepad interface (`ff/5d/01`) and a separate HID interface. The tested kernel does not automatically bind `xpad` to this receiver. Registering `10f5 7101 ff` through `xpad/new_id` makes the existing driver handle it.

- A systemd oneshot service reapplies the ID at boot.
- A narrowly scoped udev rule starts that service when the receiver is attached.
- The helper leaves the separate HID interface and other controllers alone.
- Files live under `/etc`, so ordinary distribution updates should preserve them.
- Each invocation uses the running kernel's `xpad`; it has no compiled dependency on an older kernel.
- When the receiver is already bound to `xpad`, the helper leaves it alone.

A future incompatible `xpad` change, a missing module, a changed USB ID or a system reinstall can still require an update. This does not guarantee compatibility with every future kernel. Manually unloading and reloading `xpad` while the receiver stays attached requires `sudo systemctl start nm-stealth-pivot-xpad.service` again.

Installed configuration:

```text
/etc/stealth-pivot/bind-xpad
/etc/systemd/system/nm-stealth-pivot-xpad.service
/etc/udev/rules.d/71-nm-stealth-pivot-xpad.rules
```

## Validation and scope

**Observed on Bazzite 44, kernel `7.2.11-ogc4.1.fc44.x86_64`:**

- USB receiver `10f5:7101` initially had no gamepad driver attached.
- Registering the ID bound `xpad` to its gamepad interface while retaining `usbhid` on the other interface.
- Linux created `event` and `js` gamepad devices.
- Steam detected the controller and loaded its button, stick and trigger mapping.

The initial installed configuration was tested on this hardware. The repository also has isolated helper tests, shell syntax checks and a systemd unit check. **A reboot, USB replug, distribution upgrade and full input/rumble test have not yet been validated for this repository version.**

SteamOS, Arch/CachyOS, Fedora and other systemd distributions are candidates, not hardware-tested support claims. Bluetooth and direct wired operation use different device IDs/protocols and are outside this workaround's scope. Headset audio, advanced profiles, extra buttons and firmware updates are not provided by this project.

If it does not work, attach the output of `bash status.sh` and:

```bash
journalctl -b -u nm-stealth-pivot-xpad.service --no-pager
```

Include your distribution, kernel, USB ID and connection type. Do not attach account credentials or unrelated logs.

## Native kernel support

Long term, the receiver should be added to the upstream `xpad` device tables so this workaround is unnecessary. No kernel patch is installed here, and this project does not claim upstream acceptance.

References: [Linux xpad source](https://github.com/torvalds/linux/blob/master/drivers/input/joystick/xpad.c), [USB dynamic driver IDs](https://www.kernel.org/doc/Documentation/ABI/testing/sysfs-bus-usb), [Turtle Beach Stealth Pivot](https://www.turtlebeach.com/products/stealth-pivot-controller).

Maintained by [Necrosiak](https://github.com/Necrosiak). Unofficial community project, not affiliated with Turtle Beach.

MIT license for this project's scripts and configuration; the Linux driver retains its own license.

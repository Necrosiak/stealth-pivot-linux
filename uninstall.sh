#!/usr/bin/env bash
set -euo pipefail
[[ $EUID == 0 ]] || { echo "Run: sudo bash uninstall.sh" >&2; exit 1; }
state=/var/lib/stealth-pivot-linux
[[ -f $state/installed ]] || { echo "No installation record found; nothing removed."; exit 0; }
systemctl disable --now nm-stealth-pivot-xpad.service
for path in /etc/stealth-pivot/bind-xpad /etc/systemd/system/nm-stealth-pivot-xpad.service /etc/udev/rules.d/71-nm-stealth-pivot-xpad.rules; do
    rm -f "$path"
    if [[ -e $state/original/$(basename "$path") ]]; then
        cp -a "$state/original/$(basename "$path")" "$path"
    fi
done
rmdir /etc/stealth-pivot 2>/dev/null || true
systemctl daemon-reload
udevadm control --reload-rules
if [[ -f $state/was-enabled ]]; then
    systemctl enable nm-stealth-pivot-xpad.service
fi
# Keep backups for manual inspection; allow a clean future installation.
rm -f "$state/installed" "$state/was-enabled"
echo "Uninstalled; pre-existing configuration restored. Backups kept in $state/original."
echo "An already connected controller is left working. Reboot to clear in-memory registration."

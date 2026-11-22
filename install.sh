#!/usr/bin/env bash
set -euo pipefail
[[ $EUID == 0 ]] || { echo "Run: sudo bash install.sh" >&2; exit 1; }
source_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
for command in systemctl udevadm modprobe modinfo flock install; do
    command -v "$command" >/dev/null || { echo "Missing required command: $command" >&2; exit 1; }
done
[[ -d /run/systemd/system ]] || { echo "This installer requires a running systemd system." >&2; exit 1; }
modinfo xpad >/dev/null || { echo "The running kernel does not provide xpad. Install your distribution's kernel modules first." >&2; exit 1; }
for file in bind-xpad nm-stealth-pivot-xpad.service 71-nm-stealth-pivot-xpad.rules; do
    [[ -f $source_dir/files/$file ]] || { echo "Missing files/$file. Clone the entire repository first." >&2; exit 1; }
done
# Preserve the original files once, including an earlier local workaround.
state=/var/lib/stealth-pivot-linux
mkdir -p "$state/original" /etc/stealth-pivot
paths=(/etc/stealth-pivot/bind-xpad /etc/systemd/system/nm-stealth-pivot-xpad.service /etc/udev/rules.d/71-nm-stealth-pivot-xpad.rules)
if [[ ! -f $state/installed ]]; then
    # Keep older uninstall backups without restoring stale files on a new install.
    if [[ -n $(ls -A "$state/original") ]]; then
        mv "$state/original" "$state/original-$(date +%Y%m%d-%H%M%S)-$$"
        mkdir -p "$state/original"
    fi
    systemctl is-enabled --quiet nm-stealth-pivot-xpad.service 2>/dev/null && touch "$state/was-enabled"
    for path in "${paths[@]}"; do
        [[ ! -e $path ]] || cp -a "$path" "$state/original/$(basename "$path")"
    done
    touch "$state/installed"
fi
install -m 755 "$source_dir/files/bind-xpad" "${paths[0]}"
install -m 644 "$source_dir/files/nm-stealth-pivot-xpad.service" "${paths[1]}"
install -m 644 "$source_dir/files/71-nm-stealth-pivot-xpad.rules" "${paths[2]}"
systemctl daemon-reload
udevadm control --reload-rules
systemctl enable nm-stealth-pivot-xpad.service
systemctl start nm-stealth-pivot-xpad.service
echo "Installed. Registration runs at boot and when the receiver is plugged in."
echo "A successful oneshot service normally shows inactive (dead)."
echo "Original configuration saved in $state/original."
"$source_dir/status.sh"

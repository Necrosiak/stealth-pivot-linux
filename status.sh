#!/usr/bin/env bash
set -euo pipefail
printf 'Kernel: '; uname -r
printf 'Boot registration: '; systemctl is-enabled nm-stealth-pivot-xpad.service 2>/dev/null || true
found=0
for iface in /sys/bus/usb/devices/*:*; do
    parent=${iface%:*}
    [[ $(cat "$parent/idVendor" 2>/dev/null) == 10f5 ]] || continue
    [[ $(cat "$parent/idProduct" 2>/dev/null) == 7101 ]] || continue
    found=1
    printf '%s: %s\n' "${iface##*/}" "$(basename "$(readlink "$iface/driver" || true)")"
done
[[ $found == 1 ]] || echo 'Receiver 10f5:7101 is not connected.'
if [[ -r /proc/bus/input/devices ]]; then
    awk 'BEGIN { RS="" } /Vendor=10f5 Product=7101/ { print }' /proc/bus/input/devices
fi

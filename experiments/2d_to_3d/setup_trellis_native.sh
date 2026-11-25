#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$(realpath "$0")")/trellis_env.sh"
mkdir -p "$LAB/downloads/trellis-native" "$LAB/tools/trellis-native"
cd "$LAB/downloads/trellis-native"
# Extract into E: only: no apt install, sudo, or changes to WSL's system image.
apt-get download libusb-1.0-0
for package in libusb-1.0-0_*.deb; do
    dpkg-deb -x "$package" "$LAB/tools/trellis-native"
done

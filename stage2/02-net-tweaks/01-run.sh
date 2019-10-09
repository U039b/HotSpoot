#!/bin/bash -e

install -v -d					"${ROOTFS_DIR}/etc/systemd/system/dhcpcd.service.d"
install -v -m 644 files/wait.conf		"${ROOTFS_DIR}/etc/systemd/system/dhcpcd.service.d/"

install -v -d					"${ROOTFS_DIR}/etc/wpa_supplicant"
install -v -m 600 files/wpa_supplicant.conf	"${ROOTFS_DIR}/etc/wpa_supplicant/"

if [ -v WPA_COUNTRY ]; then
	echo "country=${WPA_COUNTRY}" >> "${ROOTFS_DIR}/etc/wpa_supplicant/wpa_supplicant.conf"
fi

if [ -v WPA_ESSID ] && [ -v WPA_PASSWORD ]; then
on_chroot <<EOF
wpa_passphrase "${WPA_ESSID}" "${WPA_PASSWORD}" >> "/etc/wpa_supplicant/wpa_supplicant.conf"
EOF
fi

# Disable wifi on 5GHz models
mkdir -p "${ROOTFS_DIR}/var/lib/systemd/rfkill/"
echo 1 > "${ROOTFS_DIR}/var/lib/systemd/rfkill/platform-3f300000.mmc:wlan"
echo 1 > "${ROOTFS_DIR}/var/lib/systemd/rfkill/platform-fe300000.mmc:wlan"

# HotSpoot routing
install -v -d					"${ROOTFS_DIR}/etc/dnsmasq.d"
install -v -m 600 files/dnsmasq.conf	"${ROOTFS_DIR}/etc/dnsmasq.d/hotspoot.conf"

install -v -m 600 files/hotspoot.py	"${ROOTFS_DIR}/home/pi/hotspoot.py"
mkdir -p "${ROOTFS_DIR}/etc/network/interfaces.d"
install -v -m 600 files/eth1	"${ROOTFS_DIR}/etc/network/interfaces.d/eth1"

mkdir -p "${ROOTFS_DIR}/etc/iptables"
install -v -m 600 files/rules.v4	"${ROOTFS_DIR}/etc/iptables/rules.v4"

echo "net.ipv4.ip_forward=1" > "${ROOTFS_DIR}/etc/sysctl.conf"

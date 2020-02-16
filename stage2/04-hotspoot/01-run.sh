#!/bin/bash -e

# HotSpoot routing
install -v -d					        "${ROOTFS_DIR}/etc/dnsmasq.d"
install -v -m 600 files/dnsmasq.conf	"${ROOTFS_DIR}/etc/dnsmasq.d/hotspoot.conf"

# HotSpoot WiFi
install -v -m 600 files/hostapd.conf	"${ROOTFS_DIR}/etc/hostapd/hostapd.conf"

install -v -m 600 files/hotspoot.py	    "${ROOTFS_DIR}/home/pi/hotspoot.py"
# install -v -m 600 files/hotspoot-dashboard.json	    "${ROOTFS_DIR}/home/pi/hotspoot-dashboard.json"

mkdir -p "${ROOTFS_DIR}/etc/network/interfaces.d"
install -v -m 600 files/wlan1	        "${ROOTFS_DIR}/etc/network/interfaces.d/wlan1"

mkdir -p "${ROOTFS_DIR}/etc/iptables"
install -v -m 600 files/rules.v4	    "${ROOTFS_DIR}/etc/iptables/rules.v4"

echo "net.ipv4.ip_forward=1" >          "${ROOTFS_DIR}/etc/sysctl.conf"

# Install InfluxDB and Grafana
on_chroot <<EOF
curl -sL https://repos.influxdata.com/influxdb.key | apt-key add -
echo "deb https://repos.influxdata.com/debian stretch stable" | tee /etc/apt/sources.list.d/influxdb.list
apt-get update
apt-get install -y influxdb chronograf python3-influxdb
systemctl enable influxdb
pip3 install pyshark python-geoip-geolite2 python-geoip-python3 geoip2
wget https://dl.grafana.com/oss/release/grafana_6.4.2_armhf.deb
dpkg -i grafana_6.4.2_armhf.deb
rm -f grafana_6.4.2_armhf.deb
systemctl enable grafana-server
grafana-cli plugins install grafana-worldmap-panel
EOF

# GeoIP
install -v -m 600 files/GeoLite2-ASN.mmdb	    "${ROOTFS_DIR}/home/pi/GeoLite2-ASN.mmdb"

# Grafana configuration
install -v -m 600 files/grafana.ini	            "${ROOTFS_DIR}/etc/grafana/grafana.ini"

mkdir -p "${ROOTFS_DIR}/etc/grafana/provisioning/datasources"
install -v -m 600 files/datasources.yml	        "${ROOTFS_DIR}/etc/grafana/provisioning/datasources/datasources.yml"

mkdir -p "${ROOTFS_DIR}/etc/grafana/provisioning/dashboards"
install -v -m 600 files/dashboards.yml	        "${ROOTFS_DIR}/etc/grafana/provisioning/dashboards/dashboards.yml"

mkdir -p "${ROOTFS_DIR}/var/lib/grafana/dashboards"
install -v -m 600 files/hotspoot-dashboard.json	 "${ROOTFS_DIR}/var/lib/grafana/dashboards/hotspoot-dashboard.json"

# InfluxDB configuration
install -v -m 600 files/influxdb.conf	         "${ROOTFS_DIR}/etc/influxdb/influxdb.conf"
#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from collections import namedtuple
import re
import sys
import subprocess
import logging
import netifaces

root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - HotSpoot - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

class IFace:
    def __init__(self, name, mac, ip):
        self.name = name
        self.mac = mac
        self.ip = ip
    
    def is_apipa(self):
        return '169.254.' in self.ip

    def is_eth(self):
        return 'eth' in self.name
    
    def __repr__(self):
        return str(self.__dict__)

def get_interfaces(external=False, ip=False):
    result = []
    ifaces = netifaces.interfaces()
    for i in ifaces:
        if 'lo' == i:
            continue
        addrs = netifaces.ifaddresses(i)
        try:
            iface = IFace(i, addrs[netifaces.AF_LINK][0]['addr'], addrs[netifaces.AF_INET][0]['addr'])
            result.append(iface)
        except:
            pass
    return result

def is_apipa(iface):
    return '169.254.' in iface.ip

def get_apipa_iface(ifs):
    for interface in interfaces:
        if is_apipa(interface):
            logging.info('One APIPA interface found: %s', interface.name)
            return interface
    raise Exception('No APIPA interface found')

def get_wan_iface(ifs):
    wan_name = subprocess.check_output("/sbin/ip route get 8.8.8.8 | /bin/grep -Po '(?<=(dev )).*(?= src| proto)'", shell=True).decode()
    for interface in interfaces:
        if interface.name in wan_name:
            logging.info('One WAN interface found: %s', interface.name)
            return interface
    raise Exception('No WAN interface found')

def configure_wlan(iface):
    cmd = 'ifconfig {0} 10.0.0.1 netmask 255.255.0.0 up'.format(iface.name)
    try:
        subprocess.check_output(cmd, shell=True).decode()
    except subprocess.CalledProcessError as exc:
        raise Exception('Unable to configure WLAN interface %s - %s code returned', iface.name, exc.returncode)

def configure_ip_forward():
    cmd = 'echo 1 > /proc/sys/net/ipv4/ip_forward'
    try:
        subprocess.check_output(cmd, shell=True).decode()
    except subprocess.CalledProcessError as exc:
        raise Exception('Unable to configure IP forwarding - %s code returned', iface.name, exc.returncode)

def exec_cmd(cmd):
    try:
        subprocess.check_output(cmd, shell=True).decode()
    except subprocess.CalledProcessError as exc:
        raise Exception('Unable to execute %s - %s code returned', cmd, exc.returncode)


if __name__ == "__main__":
    root.info("HotSpoot by U+039b - https://esther.codes")
    root.info("Get network interfaces")
    interfaces = get_interfaces(external=True, ip=True)
    root.info("%s network interfaces found", len(interfaces))
    if len(interfaces) < 2:
        root.fatal('Bad number of network interfaces')
        sys.exit(1)
    for interface in interfaces:
        # print is_apipa(interface)
        root.info("{name}: {ip}".format(name=interface.name, ip=interface.ip))
    wlan=None
    try:
        wlan = get_apipa_iface(interfaces)
    except Exception as e:
        root.fatal(str(e))
        sys.exit(1)
    root.info('WLAN interface is %s', wlan.name)

    wan=None
    try:
        wan = get_wan_iface(interfaces)
    except Exception as e:
        root.fatal(str(e))
        sys.exit(1)
    root.info('WAN interface is %s', wan.name)

    try:
        configure_wlan(wlan)
    except Exception as e:
        root.fatal(str(e))
        sys.exit(1)
    root.info('WLAN interface [%s] configured', wlan.name)

    try:
        configure_ip_forward()
    except Exception as e:
        root.fatal(str(e))
        sys.exit(1)
    root.info('IP forwarding configured')

    cmd1 = '/sbin/iptables -t nat -A POSTROUTING -o {0} -j MASQUERADE'.format(wan.name)
    cmd2 = '/sbin/iptables -A FORWARD -i {0} -o {1} -m state --state RELATED,ESTABLISHED -j ACCEPT'.format(wan.name, wlan.name)
    cmd3 = '/sbin/iptables -A FORWARD -i {0} -o {1} -j ACCEPT'.format(wlan.name, wan.name)
    try:
        exec_cmd(cmd1)
        exec_cmd(cmd2)
        exec_cmd(cmd3)
    except Exception as e:
        root.fatal(str(e))
        sys.exit(1)
    root.info('Routing configured')
    
    cmd = 'systemctl restart dnsmasq'
    try:
        exec_cmd(cmd)
    except Exception as e:
        root.fatal(str(e))
        sys.exit(1)
    root.info('DHCP server restarted')

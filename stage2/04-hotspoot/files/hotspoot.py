#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from influxdb import InfluxDBClient
from geoip import geolite2
from random import randint
import geoip2.database
import pyshark
import sys
import socket
import time

class HotSpoot:
    def __init__(self):
        # InfluxDB config
        self.db = 'hotspoot'
        self.client = InfluxDBClient('localhost', 8086, 'root', 'root', self.db)
        self.client.create_database(self.db)
    
    def sniff(self, pkt):
        def org_lookup(ip):
            with geoip2.database.Reader('/home/pi/GeoLite2-ASN.mmdb') as reader:
                response = reader.asn(ip)
                return response.autonomous_system_organization
        try:
            if pkt.dns.qry_type and pkt.dns.resp_type:
                # DNS query
                dns_qry = str(pkt.dns.qry_name)
                
                # DNS source
                dns_ip_src = str(pkt.ip.dst)
                
                # DNS resolver
                dns_ip_dst = str(pkt.ip.src)
                
                # DNS A record
                dns_a = str(pkt.dns.a)

                print("%s asked for %s to %s -> %s" % (dns_ip_src, dns_qry, dns_ip_dst, dns_a))

                # Geo IP
                country = 'Unknown'
                match = geolite2.lookup(dns_a) 
                if match:
                    country = match.country

                body = {
                    "measurement": "dns_query",
                    "tags": {
                        "client": dns_ip_src,
                        "resolved": dns_a,
                        "request": dns_qry,
                        "organization": org_lookup(dns_a),
                        "country": country
                    },
                    "fields": {
                        "value": 1
                    }
                }
                r = self.client.write_points([body], database=self.db)
                
        except AttributeError:
            pass
        except Exception as e:
            print(e)
        return     


sniffer = HotSpoot()

cap = pyshark.LiveCapture(interface='wlan1')
cap.apply_on_packets(sniffer.sniff)

import json
import socket
import requests
from config import *
import os


dns_url_header = 'http://'
headers = {'content-type': 'application/json'}


def dns_hello():
    # connect to dns
    global dns_url_header

    if DNS_IsSSL:
        dns_url_header = 'https://'

    dns_host = dns_url_header + DNS_HOST_IP + ':' + str(DNS_HOST_PORT)

    endpoint = dns_host + '/hello'

    host_name = socket.gethostname()
    # host_ip = socket.gethostbyname(host_name)
    host_ip = get_lan_ip()

    payload = {'ip': host_ip}

    response = requests.post(endpoint, data=json.dumps(payload), headers=headers).json()
    return response['message']


def dns_nodes_get():
    global dns_url_header

    if DNS_IsSSL:
        dns_url_header = 'https://'

    dns_host = dns_url_header + DNS_HOST_IP + ':' + str(DNS_HOST_PORT)

    endpoint = dns_host + '/peers'

    response = requests.get(endpoint, headers=headers).json()

    return response['message']


if os.name != "nt":
    import fcntl
    import struct
    def get_interface_ip(ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
                s.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack('256s', bytes(ifname[:15], 'utf-8'))
                # Python 2.7: remove the second argument for the bytes call
            )[20:24])


def get_lan_ip():
    ip = socket.gethostbyname(socket.gethostname())
    if ip.startswith("127.") and os.name != "nt":
        interfaces = ["eth0","eth1","eth2","wlan0","wlan1","wifi0","ath0","ath1","ppp0"]
        for ifname in interfaces:
            try:
                ip = get_interface_ip(ifname)
                break
            except IOError:
                pass
    return ip
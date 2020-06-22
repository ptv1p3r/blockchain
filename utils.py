import json
import socket
import requests
from config import *
import netifaces as ni


dns_url_header = 'http://'
headers = {'content-type': 'application/json'}


def dns_hello():
    # connect to dns
    global dns_url_header

    host_ip = None

    if DNS_IsSSL:
        dns_url_header = 'https://'

    dns_host = dns_url_header + DNS_HOST_IP + ':' + str(DNS_HOST_PORT)

    endpoint = dns_host + '/hello'

    ifaces = ni.gateways()['default'][ni.AF_INET][1]
    host_ip = ni.ifaddresses(ifaces)[ni.AF_INET][0]['addr']

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




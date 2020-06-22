import json
import socket
import requests
from config import *

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
    host_ip = socket.gethostbyname(host_name)

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

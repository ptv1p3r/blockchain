from flask import Blueprint, jsonify
from os import path
from bitcoinutils.setup import setup
from bitcoinutils.keys import PrivateKey
from dns.config import *
from flask import request
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
from datetime import datetime
import requests
import json
import base64
import socket
import os.path
from threading import Timer

dnsRoute = Blueprint('dnsRoute', __name__)

PEERS = []


def ttl():
    global PEERS
    for element in PEERS:
        ip = element['ip']
        ping_ip(ip)

    Timer(TTL_TIME, ttl).start()


def ping_ip(ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)

    if ip is not None:
        try:
            if s.connect((ip, int(PEER_PORT))):
                s.shutdown(socket.SHUT_RDWR)

            header = 'http://'
            host = header + ip + ':' + str(PEER_PORT)
            endpoint = host + '/alive'

            response = requests.get(endpoint)

            if response.status_code != 201:
                removePeer_ip(ip)

        except:
            removePeer_ip(ip)

        finally:
            s.close()


def content_encrypt(data):
    # Verifica a chave publica
    recipient_key = RSA.import_key(open("keys/receiver.pem").read())
    session_key = get_random_bytes(16)
    # Encripta a chave de sessão com a chave RSA public
    cipher_rsa = PKCS1_OAEP.new(recipient_key)
    enc_session_key = cipher_rsa.encrypt(session_key)
    # Encripta os dados com a chave de sessão AES
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(data)
    # Encode em base64
    enc_session_key = base64.b64encode(enc_session_key)
    cipher_aes = base64.b64encode(cipher_aes.nonce)
    tag = base64.b64encode(tag)
    ciphertext = base64.b64encode(ciphertext)
    # Decode da chave para ir apenas o conteudo
    enc_session_key = enc_session_key.decode("utf-8")
    cipher_aes = cipher_aes.decode("utf-8")
    tag = tag.decode("utf-8")
    ciphertext = ciphertext.decode("utf-8")
    # String completa
    content = str(enc_session_key), str(cipher_aes), str(tag), str(ciphertext)
    s = ','
    msg = format(s.join(content))
    return msg


def content_decrypt(data):
    # importa a chave privada
    private_key = RSA.import_key(open("keys/private.pem").read())
    # Separação dos dados recebidos
    enc_session_key, nonce, tag, ciphertext = data.split(',')
    enc_session_key = base64.b64decode(enc_session_key.encode("utf-8"))
    nonce = base64.b64decode(nonce.encode("utf-8"))
    tag = base64.b64decode(tag.encode("utf-8"))
    ciphertext = base64.b64decode(ciphertext.encode("utf-8"))
    # Desencripta a chave de sessão com a chave privada RSA
    cipher_rsa = PKCS1_OAEP.new(private_key)
    session_key = cipher_rsa.decrypt(enc_session_key)
    # Desencripta os dados com a chave de sessão AES
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    data = cipher_aes.decrypt_and_verify(ciphertext, tag)
    # Formatação do output
    data = str(data, 'utf-8')
    data = data.replace('"', "")
    return data


def address_encrypt(ip):
    setup('mainnet')
    priv = PrivateKey(secret_exponent=1)
    message = str(ip)
    signature = priv.sign_message(message)
    return signature


def ip_to_address(ip):
    try:
        pear = next(filter(lambda x: x['ip'] == ip, PEERS), None)
        return {'bitcoin_address': pear['bitcoin_address']}
    except:
        return {'message': 'Ip não corresponde a nenhum endereço'}


def address_to_ip(address):
    try:
        pear = next(filter(lambda x: x['bitcoin_address'] == address, PEERS), None)
        return {'ip': pear['ip']}
    except:
        return {'message': 'Endereço não corresponde a nenhum ip'}


def remove_peer(bit_address):
    global PEERS
    PEERS = list(filter(lambda x: x['bitcoin_address'] != bit_address, PEERS))
    return PEERS


def removePeer_ip(ip):
    global PEERS
    PEERS = list(filter(lambda x: x['ip'] != ip, PEERS))


def generateKeys():
    # Define corretamente os caminhos onde as keys vão ser guardadas
    app_root = os.path.dirname(os.path.abspath(__file__))
    keysPath = os.path.join(app_root, 'keys')
    privateKeyPath = os.path.join(keysPath, 'private.pem')
    publicKeyPath = os.path.join(keysPath, 'receiver.pem')
    key = RSA.generate(2048)
    # Gera uma chave privada e armazena no ficheiro "private.pem"
    private_key = key.export_key()
    file_out = open(privateKeyPath, "wb")
    file_out.write(private_key)
    file_out.close()
    # Gera uma chave publica e armazena no ficheiro "reciever.pem"
    public_key = key.publickey().export_key()
    file_out = open(publicKeyPath, "wb")
    file_out.write(public_key)
    file_out.close()


def keysVerify():
    # Define corretamente os caminhos onde as keys vão ser guardadas
    app_root = os.path.dirname(os.path.abspath(__file__))
    keysPath = os.path.join(app_root, 'keys')
    privateKeyPath = os.path.join(keysPath, 'private.pem')
    publicKeyPath = os.path.join(keysPath, 'receiver.pem')
    # verifica se a pasta keys existe, se não, então é criada
    if not path.exists(privateKeyPath):
        os.makedirs(keysPath)
    # verifica se as chaves existem
    if not path.exists(privateKeyPath) or not path.exists(publicKeyPath):
        generateKeys()


@dnsRoute.route('/hello', methods=['POST'])
def hello():
    try:
        keysVerify()
        data = request.get_json()
        if data is not None:
            jsonModel = data.get('ip')
            jsonFormat = json.dumps(jsonModel, ensure_ascii=False).encode('utf8')
            # Adiciona o 1° argumento a data
            data = jsonFormat
            content = address_encrypt(data)
            data = str(data, 'utf-8')
            data = data.replace('"', "")
            now = str(datetime.now())
            if next(filter(lambda x: x['ip'] == data, PEERS), None):
                return jsonify({'ok': False, 'message': format(content)}), 200
            elif next(filter(lambda x: x['bitcoin_address'] == content, PEERS), None):
                return jsonify({'ok': False, 'message': format(content)}), 200
            else:
                pear = {'bitcoin_address': content, 'ip': data, 'timestamp': now}
                PEERS.append(pear)
                return jsonify({'ok': True, "message": format(content)}), 200
        else:
            return jsonify({'ok': False, 'message': 'Value is Empty'}), 400
    except:
        return jsonify({'ok': False, 'message': 'NOT FOUND'}), 404


@dnsRoute.route('/removePeer', methods=['POST'])
def peerCheck():
    data = request.get_json()
    bitAddress = data.get('Address')
    peers = remove_peer(bitAddress)
    return jsonify({'ok': True, "message": format(peers)}), 200


@dnsRoute.route('/PEERS', methods=['GET'])
def peersList():
    if PEERS is not None:
        try:
            return jsonify({'ok': True, "message": PEERS}), 200
        except TypeError:
            return jsonify({'ok': False, "message": 'List Not Found'}), 400


@dnsRoute.route('/dnsresolution/<address>', methods=['GET'])
def dnsResolution(address):
    try:
        return jsonify({'ok': True, "message": format(address)}), 200
    except:
        return jsonify({'ok': False, "message": 'NOT FOUND'}), 404


@dnsRoute.route('/translation/address/<ip>', methods=['GET'])
def translate_address(ip):
    if ip is not None:
        try:
            msg = ip_to_address(ip)
            return jsonify({'ok': True, "message": msg}), 200
        except:
            return jsonify({'ok': False, "message": 'NOT FOUND'}), 404


@dnsRoute.route('/translation/ip/<address>', methods=['GET'])
def translate_ip(address):
    if address is not None:
        try:
            msg = address_to_ip(address)
            return jsonify({'ok': True, "message": msg}), 200
        except:
            return jsonify({'ok': False, "message": 'NOT FOUND'}), 404


@dnsRoute.route('/data/encrypt', methods=['GET'])
def encrypt_text():
    try:
        keysVerify()
        data = request.get_json()
        required_fields = ["content"]
        for field in required_fields:
            if not data.get(field):
                return "Invalid transaction data", 404
        data = data.get("content")
        jsonModel = data
        jsonFormat = json.dumps(jsonModel, ensure_ascii=False).encode('utf8')
        data = jsonFormat
        msg = content_encrypt(data)
        return jsonify({'ok': True, "message": msg}), 200
    except:
        return jsonify({'ok': False, "message": 'NOT FOUND'}), 404


@dnsRoute.route('/data/decrypt', methods=['GET'])
def decrypt_text():
    try:
        data = request.get_json()
        required_fields = ["content"]

        for field in required_fields:
            if not data.get(field):
                return "Invalid transaction data", 404

        data = data.get("content")
        msg = content_decrypt(data)

        return jsonify({'ok': True, "message": msg}), 200
    except:
        return jsonify({'ok': False, "message": 'NOT FOUND'}), 404

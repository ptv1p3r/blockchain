from Crypto.PublicKey import RSA
from flask import Blueprint, jsonify
from os import path
from bitcoinutils.setup import setup
from bitcoinutils.keys import P2pkhAddress, PrivateKey, PublicKey
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
import sched, time
import array as arr
import sys
from threading import Timer


dnsRoute = Blueprint('dnsRoute', __name__)

peers = []


def ttl_teste():
    global peers
    for element in peers:
        ip = element['ip']
        ttl(ip)

    Timer(5, ttl_teste).start()





def ttl(ip):
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

                # s.shutdown(socket.SHUT_RDWR)

            # return jsonify({'ok': True, "message": 'CONNECTED'}), 200
        except:
            removePeer_ip(ip)
            return jsonify({'ok': False, "message": 'ERROR'}), 500
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


def addressencrypt(ip):
    # always remember to setup the network
    setup('mainnet')
    # create a private key (deterministically)
    priv = PrivateKey(secret_exponent=1)
    # get the public key
    pub = priv.get_public_key()
    message = str(ip)
    signature = priv.sign_message(message)
    return signature


def ipToAddress(ip):
    try:
        pear = next(filter(lambda x: x['ip'] == ip, peers), None)
        return {'bitcoin_address': pear['bitcoin_address']}
    except:
        return {'message': 'Ip não corresponde a nenhum endereço'}


def addressToIp(address):
    try:
        pear = next(filter(lambda x: x['bitcoin_address'] == address, peers), None)
        return {'ip': pear['ip']}
    except:
        return {'message': 'Endereço não corresponde a nenhum ip'}


def removePeer(bit_address):
    global peers
    peers = list(filter(lambda x: x['bitcoin_address'] != bit_address, peers))
    return peers


# TODO: FILTRO MAL CONSTRUIDO? USAR POP / DEL

def removePeer_ip(ip):
    global peers
    peers = list(filter(lambda x: x['ip'] != ip, peers))


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
# TODO : array em que cada hello 200 que devolva o IP, colocar IP, Endereço e TimeStamp dentro do array. mas temos que verificar se já existe.
def hello():
    try:
        keysVerify()
        data = request.get_json()
        if data is not None:
            jsonModel = data.get('ip')
            jsonFormat = json.dumps(jsonModel, ensure_ascii=False).encode('utf8')
            # Adiciona o 1° argumento a data
            data = jsonFormat
            content = addressencrypt(data)
            data = str(data, 'utf-8')
            data = data.replace('"', "")
            now = str(datetime.now())
            if next(filter(lambda x: x['ip'] == data, peers), None):
                return jsonify({'ok': False, 'message': format(content)}), 200
            elif next(filter(lambda x: x['bitcoin_address'] == content, peers), None):
                return jsonify({'ok': False, 'message': format(content)}), 200
            else:
                pear = {'bitcoin_address': content, 'ip': data, 'timestamp': now}
                peers.append(pear)
                return jsonify({'ok': True, "message": format(content)}), 200
            # return jsonify({'ok': True, "message": format(content)}), 200
        else:
            return jsonify({'ok': False, 'message': 'Value is Empty'}), 400
    except:
        return jsonify({'ok': False, 'message': 'NOT FOUND'}), 404


@dnsRoute.route('/removePeer', methods=['POST'])
def peerCheck():
    data = request.get_json()
    bitAddress = data.get('Address')
    peers = removePeer(bitAddress)
    return jsonify({'ok': True, "message": format(peers)}), 200


@dnsRoute.route('/peers', methods=['GET'])
def peersList():
    if peers is not None:
        try:
            return jsonify({'ok': True, "message": peers}), 200
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
            msg = ipToAddress(ip)
            return jsonify({'ok': True, "message": msg}), 200
        except:
            return jsonify({'ok': False, "message": 'NOT FOUND'}), 404


@dnsRoute.route('/translation/ip/<address>', methods=['GET'])
def translate_ip(address):
    if address is not None:
        try:
            msg = addressToIp(address)
            return jsonify({'ok': True, "message": msg}), 200
        except:
            return jsonify({'ok': False, "message": 'NOT FOUND'}), 404


# TODO: mais de 10 linhas é função
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
        # Adiciona o 1° argumento ao conteudo do content do jsonModel
        jsonModel = data
        # Transforma o jsonModel em json e normaliza o texto para utf8
        jsonFormat = json.dumps(jsonModel, ensure_ascii=False).encode('utf8')
        # Adiciona o 1° argumento a data
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


@dnsRoute.route('/testing', methods=['GET'])
def ttl_testing():
    try:
        for element in peers:
            ip = element['ip']
            ttl(ip)

        return jsonify({'ok': True, "message": 'ok'}), 200
    except:
        return jsonify({'ok': False, "message": 'NOT FOUND'}), 404




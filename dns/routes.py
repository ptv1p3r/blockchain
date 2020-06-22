from flask import Blueprint, jsonify
from Crypto.PublicKey import RSA

import os.path
from os import path

from flask import request
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
import json
import base64
import array as arr
from datetime import datetime
import sys

from bitcoinutils.setup import setup
from bitcoinutils.keys import P2pkhAddress, PrivateKey, PublicKey

dnsRoute = Blueprint('dnsRoute', __name__)

# peers = ["'bitcoin_address': 'content'", "'ip': '192.168.1.101'", "'timestamp': datetime.time()",
#          "'bitcoin_address': 'content'", "'ip': '192.168.1.101'", "'timestamp': datetime.time() versao 2"]

peers = []




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
    # se existir apenas uma key em falta ele repoem e substitui
    # se a outra existir ele substitui para prevenir que alguma key existente esteja corrompida
    if not path.exists(privateKeyPath) or not path.exists(publicKeyPath):
        generateKeys()


@dnsRoute.route('/message/encrypt', methods=['POST'])
def encrypt():
    keysVerify()
    data = request.get_json()
    required_fields = ["content"]

    for field in required_fields:
        if not data.get(field):
            return "Invalid transaction data", 404

    # Adiciona o 1° argumento ao conteudo do content do jsonModel
    jsonModel = data.get("content")

    # Transforma o jsonModel em json e normaliza o texto para utf8
    jsonFormat = json.dumps(jsonModel, ensure_ascii=False).encode('utf8')

    # Adiciona o 1° argumento a data
    data = jsonFormat

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

    return json.dumps({"content": format(s.join(content))})


@dnsRoute.route('/message/decrypt', methods=['POST'])
def decrypt():
    data = request.get_json()
    required_fields = ["content"]

    for field in required_fields:
        if not data.get(field):
            return "Invalid transaction data", 404

    data = data.get("content")

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

    return json.dumps({"content": data})


@dnsRoute.route('/hello', methods=['POST'])
# TODO : array em que cada hello 200 que devolva o IP, colocar IP, Endereço e TimeStamp dentro do array. mas temos que verificar se já existe.
def hello():
    try:
        ip_list = []
        keysVerify()
        data = request.get_json()
        required_fields = ['ip']
        # for field in required_fields:
        #     if not data.get(field):
        #         return jsonify({'ok': False, 'message': 'Invalid transaction data'}), 400

        jsonModel = data.get('ip')
        jsonFormat = json.dumps(jsonModel, ensure_ascii=False).encode('utf8')

        # Adiciona o 1° argumento a data
        data = jsonFormat

        content = addressencrypt(data)

        pear = {'bitcoin_address': content, 'ip': '127.0.0.1', 'timestamp': 'teste'}
        peers.append(pear)
        print(peers)
        return jsonify({'ok': True, "message": format(content)}), 200
    except:
        return jsonify({'ok': False, 'message': 'Something Failed'}), 400


def addressencrypt(ip):
    # always remember to setup the network
    setup('mainnet')

    # create a private key (deterministically)
    priv = PrivateKey(secret_exponent=1)

    # compressed is the default
    # print("\nPrivate key WIF:", priv.to_wif(compressed=True))

    # could also instantiate from existing WIF key
    # priv = PrivateKey.from_wif('KwDiBf89qGgbjEhKnhxjUh7LrciVRzI3qYjgd9m7Rfu73SvHnOwn')

    # get the public key
    pub = priv.get_public_key()

    # compressed is the default
    # print("Public key:", pub.to_hex(compressed=True))

    # get address from public key
    address = pub.get_address()

    # print the address and hash160 - default is compressed address
    # print("Address:", address.to_string())
    # print("Hash160:", address.to_hash160())

    # print("\n--------------------------------------\n")

    # sign a message with the private key and verify it
    message = str(ip, 'utf-8')
    # message = "127.0.0.1:8000"
    signature = priv.sign_message(message)
    # print("The message to sign:", message)
    # print("The signature is:", signature)

    # if PublicKey.verify_message(address.to_string(), signature, message):
    #     print("The signature is valid!")
    # else:
    #     print("The signature is NOT valid!")

    return signature


@dnsRoute.route('/peers', methods=['GET'])
def peersList():
    if peers is not None:
        try:
            return jsonify({'ok': True, "message": list(peers)}), 200
        except TypeError:
            return jsonify({'ok': False, "message": 'List Not Found'}), 400




@dnsRoute.route('/dnsresolution/<address>', methods=['GET'])
def dnsResolution(address):
    try:
        return jsonify({'ok': True, "message": format(address)}), 200
    except:
        return jsonify({'ok': False, "message": 'NOT FOUND'}), 404


# TODO: METODO GET , Passas BITCOIN NODE ADDRESS E DEVOLVES IP , procurar no array, ver se existe, se sim, retornar, se nao, devolver que nao existe (not found)

from flask import Blueprint, jsonify
from Crypto.PublicKey import RSA

from flask import request
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
import json
import base64
import sys

dnsRoute = Blueprint('dnsRoute', __name__)


@dnsRoute.route('/helo')
def hello():
    return jsonify({'message': "Hello"})


@dnsRoute.route('/message/encrypt', methods=['POST'])
def encrypt():
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

    # abre o ficheiro "encrypted_data.bin" onde vai ser armazenada a informação do 1° argumento
    file_out = open("encryptedData/encrypted_data.bin", "wb")

    # Verifica a chave publica
    recipient_key = RSA.import_key(open("keys/receiver.pem").read())
    session_key = get_random_bytes(16)

    # Encripta a chave de sessão com a chave RSA public
    cipher_rsa = PKCS1_OAEP.new(recipient_key)
    enc_session_key = cipher_rsa.encrypt(session_key)

    # Encripta os dados com a chave de sessão AES
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(data)

    # TODO: Transformar array de bytes em ut8
    testeA = base64.b64encode(enc_session_key)
    testeB = cipher_aes.nonce
    testeC = tag
    testeD = ciphertext

    [file_out.write(x) for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext)]
    file_out.close()

    return json.dumps({"content": "O content foi encryptado"})


@dnsRoute.route('/message/decrypt', methods=['POST'])
def decrypt():
    data = request.get_json()
    required_fields = ["content"]

    for field in required_fields:
        if not data.get(field):
            return "Invalid transaction data", 404

    # TODO: Possivelmente no futuro temos de ir buscar a encrypt data por request (ele está a ler a do ficheiro encrypted_data.bin)
    # Abre p ficheiro onde está a data a ser desincriptada
    file_in = open("encryptedData/encrypted_data.bin", "rb")

    # importa a chave privada
    private_key = RSA.import_key(open("keys/private.pem").read())

    enc_session_key, nonce, tag, ciphertext = \
        [file_in.read(x) for x in (private_key.size_in_bytes(), 16, 16, -1)]

    # Desencripta a chave de sessão com a chave privada RSA
    cipher_rsa = PKCS1_OAEP.new(private_key)
    session_key = cipher_rsa.decrypt(enc_session_key)

    # Desencripta os dados com a chave de sessão AES
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    data = cipher_aes.decrypt_and_verify(ciphertext, tag)
    print(data.decode("utf-8"))

    return json.dumps({"conteudo": format(data.decode("utf-8"))})
# format(data.decode("utf-8"))

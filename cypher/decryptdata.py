from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
import json

# Abre p ficheiro onde está a data a ser desincriptada
file_in = open("encrypted_data.bin", "rb")

# importa a chave privada
private_key = RSA.import_key(open("private.pem").read())

enc_session_key, nonce, tag, ciphertext = \
    [file_in.read(x) for x in (private_key.size_in_bytes(), 16, 16, -1)]

# Desencripta a chave de sessão com a chave privada RSA
cipher_rsa = PKCS1_OAEP.new(private_key)
session_key = cipher_rsa.decrypt(enc_session_key)

# Desencripta os dados com a chave de sessão AES
cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
data = cipher_aes.decrypt_and_verify(ciphertext, tag)
print(data.decode("utf-8"))

# dataJson = json.dumps(data.decode("utf-8"), indent=2)
#
# print(dataJson)

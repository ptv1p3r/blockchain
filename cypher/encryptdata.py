from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
import json
import sys
import unicodedata as ud

# Adiciona o 1° argumento ao conteudo do content do jsonModel
jsonModel = {
  "content": str(sys.argv[1])
}

# Transforma o jsonModel em json e normaliza o texto para utf8
jsonFormat = json.dumps(jsonModel, ensure_ascii=False).encode('utf8')

# Adiciona o 1° argumento a data
data = jsonFormat

# abre o ficheiro "encrypted_data.bin" onde vai ser armazenada a informação do 1° argumento
file_out = open("encrypted_data.bin", "wb")

# Verifica a chave publica
recipient_key = RSA.import_key(open("receiver.pem").read())
session_key = get_random_bytes(16)

# Encripta a chave de sessão com a chave RSA public
cipher_rsa = PKCS1_OAEP.new(recipient_key)
enc_session_key = cipher_rsa.encrypt(session_key)

# Encripta os dados com a chave de sessão AES
cipher_aes = AES.new(session_key, AES.MODE_EAX)
ciphertext, tag = cipher_aes.encrypt_and_digest(data)
[file_out.write(x) for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext)]
file_out.close()

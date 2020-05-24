from Crypto.PublicKey import RSA


key = RSA.generate(2048)
# Gera uma chave privada e armazena no ficheiro "private.pem"
private_key = key.export_key()
file_out = open("private.pem", "wb")
file_out.write(private_key)
file_out.close()

# Gera uma chave publica e armazena no ficheiro "reciever.pem"
public_key = key.publickey().export_key()
file_out = open("receiver.pem", "wb")
file_out.write(public_key)
file_out.close()
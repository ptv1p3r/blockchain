from hashlib import sha256
import json
import time


class Block:
    def __init__(self, index, transactions, timestamp, previous_hash):
        self.index = index                      # Id do bloco
        self.transactions = transactions        # lista de transacoes (data)
        self.timestamp = timestamp              # timestamp de geracao do bloco
        self.previous_hash = previous_hash      # hash do ultimo bloco a ser incluido no novo bloco

    def compute_hash(self):
        # retorna a hash do bloco convertendo primeiro para uma string
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()


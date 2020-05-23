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
        # garante a ordenação do dictionary caso contrario podemos ter hashes inconsistentes
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()


class Blockchain:
    difficulty = 2  # dificuldade PoW

    def __init__(self):
        self.chain = []
        self.generate_genesis_block()

    def generate_genesis_block(self):
        # cria o bloco genesis(bloco inicial) com index a 0, previous_hash a 0 e uma hash valida
        genesis_block = Block(0, [], time.time(), "0")
        genesis_block.hash = genesis_block.compute_hash()
        # adiciona bloco à chain
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        # retorna o ultimo bloco
        return self.chain[-1]

    def proof_of_work(self, block):
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash

    def add_block(self, block, proof):
        previous_hash = self.last_block.hash

        if previous_hash != block.previous_hash:
            return False

        if not Blockchain.is_valid_proof(block, proof):
            return False

        block.hash = proof
        self.chain.append(block)
        return True

    def is_valid_proof(self, block, block_hash):
        return (block_hash.startswith('0' * Blockchain.difficulty) and
                block_hash == block.compute_hash())

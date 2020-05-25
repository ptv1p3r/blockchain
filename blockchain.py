from hashlib import sha256
import json
import time


class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        self.index = index                      # Id do bloco
        self.transactions = transactions        # lista de transacoes (data)
        self.timestamp = timestamp              # timestamp de geracao do bloco
        self.previous_hash = previous_hash      # hash do ultimo bloco a ser incluido no novo bloco
        self.nonce = nonce

    def compute_hash(self):
        # retorna a hash do bloco convertendo primeiro para uma string
        # garante a ordenação do dictionary caso contrario podemos ter hashes inconsistentes
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()


class Blockchain:
    difficulty = 2  # dificuldade PoW

    def __init__(self):
        self.unconfirmed_transactions = []  # dados nao confirmados
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

        # altera o valor nonce de forma a que o valor final da hash seja o espera com o respectivo grau de dificuldade
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash

    def add_block(self, block, proof):
        # adiciona o novo bloco à chain apos validação
        previous_hash = self.last_block.hash

        # hash do bloco e hash do ultimo bloco na chain sao diferentes
        if previous_hash != block.previous_hash:
            return False

        # valida a formatacao de bloco e hash
        if not self.is_valid_proof(block, proof):
            return False

        block.hash = proof
        self.chain.append(block)
        return True

    def is_valid_proof(self, block, block_hash):
        # valida o inicio da block hash e a respectiva hash
        return block_hash.startswith('0' * Blockchain.difficulty) and block_hash == block.compute_hash()

    def add_new_transaction(self, transaction):
        # adiciona nova transação (data) à lista de não confirmadas
        self.unconfirmed_transactions.append(transaction)

    def check_chain_validity(self, chain):
        result = True
        previous_hash = "0"

        for block in chain:
            block_hash = block.hash
            # remove o campo hash e forca a criação de uma nova hash
            delattr(block, "hash")

            if not self.is_valid_proof(block, block_hash) or previous_hash != block.previous_hash:
                result = False
                break

            block.hash, previous_hash = block_hash, block_hash

        return result

    def mine(self):
        if not self.unconfirmed_transactions:
            return False

        last_block = self.last_block

        new_block = Block(index=last_block.index + 1,
                          transactions=self.unconfirmed_transactions,
                          timestamp=time.time(),
                          previous_hash=last_block.hash)

        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)
        self.unconfirmed_transactions = []

        return new_block.index


def create_chain_from_dump(chain_dump):
    generated_blockchain = Blockchain()
    generated_blockchain.generate_genesis_block()
    for idx, block_data in enumerate(chain_dump):
        block = Block(block_data["index"],
                block_data["transactions"],
                block_data["timestamp"],
                block_data["previous_hash"])
        proof = block_data['hash']
        if idx > 0:
            added = generated_blockchain.add_block(block, proof)
            if not added:
                raise Exception("The chain is tampered!!")
            else:  # é um bloco genesis, não necessita de verificação
                generated_blockchain.chain.append(block)
    return generated_blockchain

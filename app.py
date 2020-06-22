import datetime
from flask import Flask, request
from node_server import *
import time
from utils import *
import socket

app = Flask(__name__)

blockchain = Blockchain()
blockchain.generate_genesis_block()

# host addresses of the p2p network
peers = set()
nodes = []

# # contact dns for bitcoin address
# bitcoin_node_address = dns_hello()
#
# # get node list from dns
# nodes.append(dns_nodes_get())

# if bitcoin_node_address is not None:
#     nodes.add(bitcoin_node_address)


@app.route("/")
def index():
    # contact dns for bitcoin address
    bitcoin_node_address = dns_hello()

    # get node list from dns
    nodes.append(dns_nodes_get())
    return "ISMAT 2020 Computação Distribuida : BlockChain Node" + ' {0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())


# endpoint para novas transactions(data)
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    tx_data = request.get_json()
    required_fields = ["content"]

    for field in required_fields:
        if not tx_data.get(field):
            return "Invalid transaction data", 404

    tx_data["timestamp"] = time.time()

    blockchain.add_new_transaction(tx_data)

    return "Success", 201


# enpoint que retorna uma copia da chain
@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return json.dumps({"length": len(chain_data),
                       "chain": chain_data,
                       "peers": list(peers)})


# enpoint que efetua o mine das transaction nao confirmadas
@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    result = blockchain.mine()
    if not result:
        return "No transactions to mine"
    else:
        # garante que temos a maior chain antes de a anunciar à rede
        chain_length = len(blockchain.chain)
        consensus()
        if chain_length == len(blockchain.chain):
            # anuncia o bloco minado mais recente à rede
            announce_new_block(blockchain.last_block)
        return "Block #{} is mined.".format(blockchain.last_block.index)


# enpoint que retorna transactions nao confirmadas
@app.route('/transactions/unconfirmed')
def get_pending_tx():
    return json.dumps(blockchain.unconfirmed_transactions)


# endpoint para adicionar um bloco minado por um no ao chain
@app.route('/block/add', methods=['POST'])
def verify_and_add_block():
    block_data = request.get_json()
    block = Block(block_data["index"],
                  block_data["transactions"],
                  block_data["timestamp"],
                  block_data["previous_hash"],
                  block_data["nonce"])

    proof = block_data['hash']
    added = blockchain.add_block(block, proof)

    if not added:
        return "The block was discarded by the node", 400

    return "Block added to the chain", 201


# Endpoint para adicionar novos peers à rede
@app.route('/node/register', methods=['POST'])
def register_new_peers():
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400

    peers.add(node_address)

    return get_chain()


# endpoint para registo de novo nó
@app.route('/register', methods=['POST'])
def register_with_existing_node():
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400

    data = {"node_address": request.host_url}
    headers = {'Content-Type': "application/json"}

    # faz um pedido para registo com no remoto e extrai informação
    response = requests.post(node_address + "/node/register", data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        global blockchain
        global peers
        # actualiza chain e peers
        chain_dump = response.json()['chain']
        blockchain = create_chain_from_dump(chain_dump)
        peers.update(response.json()['peers'])
        return "Registration successful", 200
    else:
        return response.content, response.status_code


def create_chain_from_dump(chain_dump):
    generated_blockchain = Blockchain()
    generated_blockchain.generate_genesis_block()
    for idx, block_data in enumerate(chain_dump):
        if idx == 0:
            continue  # passa bloco genesis
        block = Block(block_data["index"],
                      block_data["transactions"],
                      block_data["timestamp"],
                      block_data["previous_hash"],
                      block_data["nonce"])
        proof = block_data['hash']
        added = generated_blockchain.add_block(block, proof)
        if not added:
            raise Exception("The chain is tampered!!")
    return generated_blockchain


def consensus():
    # se uma chain maior for encontrada é alterada
    global blockchain

    longest_chain = None
    current_len = len(blockchain.chain)

    for node in peers:
        response = requests.get('{}chain'.format(node))
        length = response.json()['length']
        chain = response.json()['chain']
        if length > current_len and blockchain.check_chain_validity(chain):
            current_len = length
            longest_chain = chain

    if longest_chain:
        blockchain = longest_chain
        return True

    return False


# anuncia os novos blocos na rede
def announce_new_block(block):
    for peer in peers:
        url = "{}block/add".format(peer)
        headers = {'Content-Type': "application/json"}
        requests.post(url, data=json.dumps(block.__dict__, sort_keys=True), headers=headers)


if __name__ == '__main__':
    app.run(debug=True, port=5000)





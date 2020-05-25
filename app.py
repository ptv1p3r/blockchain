from flask import Flask, request
import requests
import blockchain
import time
import json

app = Flask(__name__)

blockchain = blockchain.Blockchain()

# host addresses of the p2p network
peers = set()


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
                       "chain": chain_data})


# enpoint que efetua o mine das transaction nao confirmadas
@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    result = blockchain.mine()
    if not result:
        return "No transactions to mine"
    return "Block #{} is mined.".format(result)


# enpoint que retorna transactions nao confirmadas
@app.route('/transactions/unconfirmed')
def get_pending_tx():
    return json.dumps(blockchain.unconfirmed_transactions)


app.run(debug=True, port=8000)

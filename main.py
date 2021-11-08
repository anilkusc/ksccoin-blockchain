import json
from flask import Flask, jsonify, request
from uuid import uuid4
from blockchain import Blockchain

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

app = Flask(__name__)
# create my chain
myblockchain = Blockchain()
#mining endpoint
@app.route('/mine', methods=['GET'])
def mine():
    # proof of working for mining
    last_block = myblockchain.last_block()
    last_proof = last_block["proof"]
    proof = myblockchain.proof_of_work(last_proof)
    # because we adding new block, sender is 0.
    myblockchain.new_transaction(sender=0,receiver=node_identifier,amount=1)
    # hash the last block for consistency
    previous_hash = myblockchain.hash(last_block)
    # new block will be created and it will return the information of the new block.
    block = myblockchain.new_block(proof,previous_hash)
    response = {
        "message": "New Block Forged",
        "index": block["index"],
        "transactions": block["transactions"],
        "proof": block["proof"],
        "previous_hash" : block["previous_hash"]
    }

    return jsonify(response), 200
# create new transaction
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    # control if sender,reciver,amount values are specified , otherwise return error
    if values["sender"] == None or values["receiver"] == None or values["amount"] == None:
        return 'At least one of these variables are missing: sender,receiver,amount', 400
    # create new transaction on the block
    index = myblockchain.new_transaction(values["sender"],values["receiver"],values["amount"])
    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201
# get the all information of chains
@app.route('/chain', methods=['GET'])
def chain():
    response = {
        "chain": myblockchain.chain,
        "length": len(myblockchain.chain)
    }
    return jsonify(response), 200
# register a new node
@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()
    nodes = values["nodes"]
    if nodes is None:
        return "Error: There is no node in request body" , 400
    # add all wanted nodes
    for node in nodes:
        myblockchain.register_node(node)
    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(myblockchain.nodes),
    }        
    return jsonify(response), 200
# control if there is any conflict between our blockchain node and other nodes.
@app.route('/nodes/resolve', methods=['GET'])
def resolve_conflicts():
    if myblockchain.resolve_conflicts():
        response = {
            'message': 'Our chain was replaced',
            'new_chain': myblockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': myblockchain.chain
        }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
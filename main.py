import copy
from flask import Flask, jsonify, request
from uuid import uuid4
from blockchain import Blockchain
import time
from threading import Thread

#import _thread
# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')
# How long node will be wait in elected state in second.(now+election_time_range)
election_time_range = 3
# Set transaction limit. It determines how mant transaction can be there in every chain
transaction_limit = 10

app = Flask(__name__)
# create my chain
myblockchain = Blockchain()
# adding self address to nodes
myblockchain.nodes.append(myblockchain.address)
#mining endpoint.Selected node will be mining.
@app.route('/mine', methods=['POST'])
def mine():
    values = request.get_json()
    code = 200
    if values["leader"] == myblockchain.leader_control():
        # proof of working for mining
        last_block = myblockchain.chain[-1]['index'] + 1
        # hash the last block for consistency
        previous_hash = myblockchain.hash(last_block)
        # new block will be created and it will return the information of the new block.
        block = myblockchain.new_block(previous_hash)
        # because we adding new block, sender is 0.
        myblockchain.new_transaction(sender=0,receiver=values["receiver"],amount=1)
        response = {
            "message": "New Block Forged",
            "index": block["index"],
            "transactions": block["transactions"],
            "previous_hash" : block["previous_hash"]
        }
    else:
        response = {'message': f'Leader is not legit.'}
        code = 400
    return jsonify(response), code
# create new transaction
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    if myblockchain.elect_state == True:
        response = {'message': f'Chain is currently in elect state.Please wait...'}
        return jsonify(response), 301
    values = request.get_json()
    # control if sender,reciver,amount values are specified , otherwise return error
    if values["sender"] == None or values["receiver"] == None or values["amount"] == None:
        return 'At least one of these variables are missing: sender,receiver,amount', 400
    # create new transaction on the block
    index = myblockchain.new_transaction(values["sender"],values["receiver"],values["amount"])
    # If record count is reach to 10 , all chain is stop transactions immediately,
    # they have synchronize all transactions and starte elections state.
    # After election on of the node would be elect for creating new block and transactions are continue.
    if len(myblockchain.transactions) > transaction_limit:
        response = {'message': f'Transaction will be added to Block {index}. The transaction limit has been reached for this block. New Block will be created in short time.'}
        myblockchain.elect_state = True
        myblockchain.election_deadline = round(time.time()) + election_time_range
        Thread(target = myblockchain.declare_leader_control ).start()
    else:
        response = {'message': f'Transaction will be added to Block {index}.'}
    return jsonify(response), 201
# get the all information of chains
@app.route('/chain', methods=['GET'])
def chain():
    # because of showin transaction on the not sealed chain we need to copy myblockchain object, append 
    mock_chain = copy.deepcopy(myblockchain)
    mock_chain.new_block(previous_hash="not_sealed")
    response = {
        "chain": mock_chain.chain,
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
# This functions is resposible for get votes from nodes. They are collected in a list and 
@app.route('/election/vote', methods=['POST'])
def election():
    values = request.get_json()
    code = 400
    # if nodes are not in elect state, voting is not permitted.
    if round(time.time()) > myblockchain.election_deadline or myblockchain.elect_state == False:
        response = {'message': 'Election time has been finished:'}
    # vote should be valid    
    elif values["node"] == None or values["vote"] == None:
        response = {'message': 'Vote is invalid'}
    elif values["node"] not in myblockchain.nodes:
        response = {'message': 'Node is not registered'}
    elif values["vote"] < 0 or values["vote"] > (len(myblockchain.nodes)-1):
        response = {'message': 'Node is not registered'}
    else:
        myblockchain.elections.append(values)
        response = {'message': 'Vote is received.{values}'}
        code = 200
    return jsonify(response), code
# This func. get transaction synchronization from other nodes.
# TO-DO: transaction validation will be implemented
@app.route('/sync/transaction', methods=['POST'])
def sync_transaciton():
    values = request.get_json()
    code = 400
    if myblockchain.elect_state == False:
        response = {'message': 'The Node is in the election state:'}
    elif values["sender"] == None or values["receiver"] == None or values["amount"] == None:
        response = {'message': 'Transaction is invalid'}
    else:
        myblockchain.sync_transaction(sender=values["sender"],receiver=values["receiver"],amount=values["amount"])
        response = {'message': 'Transaction appended'}
        code = 200
    return jsonify(response), code
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
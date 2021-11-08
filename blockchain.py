import hashlib
import json
from time import time
import requests
from flask.globals import request

# Blockchain class which has all attributes of the blockchain network
class Blockchain(object):

    def __init__(self):
        # chain is array of blocks. It has index,timestamp,transactions,proof,previous_hash
        self.chain = []
        # it is all nodes in the network. When you change the network it would be changed also
        self.nodes = []
        # transactions are used for sending and receiving money. Every block record transactions. 
        # For ex. if you want to check balance of your wallet , you need to query all of your questions and get the result.
        self.transactions = []
        # Create genesis(first) block.
        self.new_block(previous_hash=0,proof=100)
    # this function adds new blocks to the chain
    def new_block(self,previous_hash,proof):
        # sealing last block. After sealing new empty new block will be added to block and this block cannot be tampered.
        block = {
            # index of the block
            "index": len(self.chain) + 1,
            # creating time as epoch time.
            "timestamp": time() ,
            # all transactions of the last block.
            "transactions": self.transactions,
            # proof of the block
            "proof": proof,
            # hash of the previous block. If you change anything on any block all hashes will be change. So it is the proof of consistency
            "previous_hash": previous_hash
        }
        # reset transactions because last block sealed and you need o create new block
        self.transactions = []
        # add new empty block to chain
        self.chain.append(block)
        return block

    # this function creates new transaction
    def new_transaction(self,sender,receiver,amount):
        #add a new transaction to current block.
        self.transactions.append({
            # sender wallet code
            "sender": sender,
            # receiver wallet code
            "receiver": receiver,
            # amount
            "amount": amount,
        })
        # return next blocks index
        return self.last_block()['index'] + 1
    # return last block of the blockchain
    def last_block(self):
        return self.chain[-1]
    # hash the all block
    def hash(self,block):
        block_string = json.dumps(block,sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    # proof of work mining
    def proof_of_work(self,last_proof):
        # try all possibilites and brute force to proof
        proof = 0
        while self.valid_proof(last_proof,proof) is False:
            proof = proof + 1
        # when you find the proof return it
        return proof
    # validation of the proof
    def valid_proof(self,last_proof,proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"
    # just add node to nodes array
    def register_node(self, address):
        self.nodes.append(address)
    # control new nodes chain(think like a database) if it is valid
    def valid_node(self,chain):
        # control every single block previous_hash in the block chain.
        control_block = chain[0]
        for block in chain:
            if block["previous_hash"] != self.hash(control_block):
                return False
            if not self.valid_proof(control_block['proof'], block['proof']):
                return False
        return True
    # Consensus Algorithm. For now it longest one would be winner and the longest one would be authorative
    def resolve_conflicts(self):
        # get neighbours from nodes array
        neighbours = self.nodes
        new_chain = None
        # We're only looking for chains longer than ours
        max_length = len(self.chain)
        # control every node 
        for node in neighbours:
            response = requests.get( node+"/chain" )
            # if node responded with code 200 look at the length and chain
            if response.status_code == 200:
                # get neighbour's chain length and chains.
                length = response.json()['length']
                chain = response.json()['chain']
            # If nighbours node is longer than ours we consider it authoritive node and replicate information from the neighbour.
            if self.valid_node(chain) and length > max_length:
                new_chain = chain
                max_length = len(new_chain)
        if new_chain:
            self.chain = new_chain
            return True
        return False
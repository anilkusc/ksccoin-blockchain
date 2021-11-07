import hashlib
import json
from time import time
import requests
from flask.globals import request

class Blockchain(object):

    def __init__(self):
        self.chain = []
        self.nodes = []
        self.transactions = []
        self.new_block(previous_hash=0,proof=100)

    def new_block(self,previous_hash,proof):
        block = {
            "index": len(self.chain) + 1, 
            "timestamp": time() ,
            "transactions": self.transactions,
            "proof": proof,
            "previous_hash": previous_hash
        }
        self.transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self,sender,receiver,amount):
        self.transactions.append({
            "sender": sender,
            "receiver": receiver,
            "amount": amount,
        })
        return self.last_block()['index'] + 1
        
    def last_block(self):
        return self.chain[-1]

    def hash(self,block):
        block_string = json.dumps(block,sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    

    def proof_of_work(self,last_proof):
        proof = 0
        while self.valid_proof(last_proof,proof) is False:
            proof = proof + 1
        return proof

    def valid_proof(self,last_proof,proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def register_node(self, address):
        self.nodes.append(address)
    # the longest is valid
    def valid_node(self,chain):
        control_block = chain[0]
        for block in chain:
            if block["previous_hash"] != self.hash(control_block):
                return False
            if not self.valid_proof(control_block['proof'], block['proof']):
                return False
        return True
    # Consensus Algorithm. For now this is only longest one.
    def resolve_conflicts(self):
        neighbours = self.nodes
        new_chain = None
        # We're only looking for chains longer than ours
        max_length = len(self.chain)
        for node in neighbours:
            response = requests.get( node+"/chain" )
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
            if self.valid_node(chain) and length > max_length:
                new_chain = chain
                max_length = len(new_chain)
        if new_chain:
            self.chain = new_chain
            return True
        return False
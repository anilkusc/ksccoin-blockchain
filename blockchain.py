import hashlib
import json
import time
from flask.json import jsonify
import requests
from flask.globals import request
import random
import socket

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
        # it is stated for election records.
        self.elections = []
        # Create genesis(first) block.
        self.new_block(previous_hash=0)
        # get self address for node
        self.address = socket.gethostbyname(socket.gethostname())
        # when elect state true all transaction are stopped and chain create new block.
        self.elect_state = False
        # election finishes when deadline occured
        # it must be epoch time.
        self.election_deadline = 0
    # this function adds new blocks to the chain
    def new_block(self,previous_hash):
        # sealing last block. After sealing new empty new block will be added to block and this block cannot be tampered.
        block = {
            # index of the block
            "index": len(self.chain) + 1,
            # creating time as epoch time.
            "timestamp": time.time() ,
            # all transactions of the last block.
            "transactions": self.transactions,
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
            # If neighbours node is longer than ours we consider it authoritive node and replicate information from the neighbour.
            if self.valid_node(chain) and length > max_length:
                new_chain = chain
                max_length = len(new_chain)
        if new_chain:
            self.chain = new_chain
            return True
        return False
    # when transactions has been done , blockchain's state set to election state.
    # Every node elect a node randomly and stream it to the blockchain network.
    def elect_state_sender(self):
        vote = random.randint(0,len(self.nodes)-1)
        election_record = {"vote":vote,"node":self.address}
        # send every node to my vote
        for node in self.nodes:
            r = requests.post("http://"+node+":5000/election/vote", data = election_record)
            if r.status_code == 200:
                print("Stream has been sent to node:"+node)
            else:
                print("Stream could not sent to node:"+node)
    def leader_control(self):
        max = 0
        leader = self.nodes[0]
        for node in self.nodes:
            if self.nodes.count(node) > max:
                max = self.nodes.count(node)
                leader = node
            elif self.nodes.count(node) == max:
                # if vote counts are equal , select min of two nodes.
                leader = min(leader,node)
        return leader
    # this functions control if this node is leader or not.
    # If leader is ownself , send stream to network
    def declare_leader_control(self):
        while 1:
            if round(time.time()) < self.election_deadline :
                print("Chain Network is in elect state. Waiting for leader control.")
                time.sleep(5)
            else:
                self.elect_state = False
                if self.address == self.leader_control():
                    for node in self.nodes:
                        mine_data = {"leader":self.address,"receiver":self.address}
                        r = requests.post("http://"+node+":5000/mine", json = mine_data)
                        if r.status_code == 200:
                            print("Stream has been sent to node:"+node)
                        else:
                            print("Stream could not sent to node:"+node)
                print("The node is no more in elect state.")    
                break
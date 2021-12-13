# KSCCOIN-BLOCKCHAIN

:scroll:
The ksccoin-* repostories purpose create a blockchain ecosystem from scratch.This repo aims to orchestrate blockchain network. For now it is very primitive version of blockchain of ksccoin.

## API ENDPOINTS

:vertical_traffic_light:
| URI | METHOD | BODY | RESPONSE | DESCRIPTION |
| ----------- | --------------- | --------- | ----------- | ----------- |
| /mine | POST | {"leader": "<leader-ip>","receiver": "<receiver-ip>"} | {"message": "New Block Forged","index": 1,"transactions": "<transactions>","previous_hash" : "<hash>"} | Mining means creating new block on the chain.
| /transactions/new | POST | {"sender": "<sender_hash>","receiver": "<receiver_hash>","amount": 100} | {'message': f'Transaction will be added to Block {index}'} | Creating new transaction means sending and receiving money in this block.
| /chain | GET | - | {"chain": [{"index": 1,"previous_hash": 0,"proof": 100,"timestamp": <epoch_time>,"transactions": []},{"index": 2,"previous_hash": 35293,"proof": "<proof_hash>","timestamp": <epoch_time>,"transactions": [{"amount": 1,"receiver": "<receiver_address>","sender": 0}]}],"length": 2} | Get all chains and transaction informations.
| /nodes/register | POST | {"nodes": ["http://<node_ip>:<port>","http://192.168.1.100:5000"]} | {"message": "","total_nodes": ["http://<node_ip>:<port>","http://192.168.1.100:500"]} | Register a node to blockchain network.
| /nodes/resolve | GET | - | {"message": "","chain": "same as /chain"} | Sync nodes on the blockchain network.
:vertical_traffic_light:

## HOW IT WORKS

:scroll:
It is working as very simple blockchain platform. Most of the concepts are simplified for the sake of understandable. 

:scroll:
Nodes are every single machine in the p2p network. They all have same blockchain database. They have a URL and all of the nodes have all of the node's addresses.

:scroll:
Chains are made up of blocks. The blocks are connected each other like a chain. This chain is not be able to break and tamper. Because all blocks have hash of the previous block, you cannot change any block. If you change any comma,dot or something like that all hashes will be change. So it is impossible.

:scroll:
Blocks has 5 main structure. Index is index of the block. When you add new index it will be increased with 1 last index block. Timestamp is epoch time and it is equal to create time of the block. Proof is a kind of password which needs to be guess by miners. Miners find the proof and it qualifies to add new block to chain and the miner reward by a coin. Previous hash is hash of the previous block. It ensures the immunity of the chain. Transactions has a sender , receiver and amount value. So if you want to calculate your wallet or something like that you need get all transactions of your wallet and calculate the account .

:scroll:
Consensus is related with reliablity of the blockchain network. In this project it is very simple and it only accepts longest chain as authorative.

## FURTHER INFORMATION

:scroll:
While creating this repository following articles are used:

:mortar_board:
https://medium.com/blochain-crpto-defi-web3-0/the-beginner-guide-to-blockchain-ad326e1d9404

:mortar_board:
https://hackernoon.com/learn-blockchains-by-building-one-117428612f46


## TODOS

:pushpin:
Creating wallet(Another repository)(for examine wallet transacitons go until the firs wallet created.We can understand if that block sender and receiver is our wallet and amount 0 it is the first transaction that belongs to our wallet)

:pushpin:
Better consensus algorithm.

:pushpin:
Transaction validation.

:pushpin:
Improve proof of work(mining)

:pushpin:
Implement more legit validating and registering a node

:pushpin:
Propagate transactions between nodes and blockchain network with consensus

:pushpin:
Create new vallet on the block as transaction. Sender: block,receiver: new created wallet , amount 0

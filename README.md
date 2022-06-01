![Python](https://img.shields.io/github/pipenv/locked/python-version/ScruffyTheMoose/blockChain)
![Flask](https://img.shields.io/github/pipenv/locked/dependency-version/ScruffyTheMoose/blockChain/flask)
![PyQt5](https://img.shields.io/github/pipenv/locked/dependency-version/ScruffyTheMoose/blockChain/pyqt5)
![requests](https://img.shields.io/github/pipenv/locked/dependency-version/ScruffyTheMoose/blockChain/requests)

## About
`blockChain` is a private blockchain built from scratch using **Python** and **Flask** purely to learn about this popular decentralized technology. Through a dynamic network of nodes, this private blockchain can facilitate transactions and mint new blocks all while maintaining consensus. All operations on the network are validated using unique node IDs, a proofing algorithm for each block, and a consensus algorithm. Because each node is controlled exclusively through network requests, it is extremely easy to automate operations.

## User Interface
In addition to the private blockchain, I built a simple GUI using **PyQt5** for controlling node operations and interactions to make sending GET and POST requests easier while working with the network. A user can select which node to send a request to, the type of request, and any POST-required input. An "observer" node on the network is tied directly to the GUI which will keep track of any changes to each individual node.
![GUI Demo Image](https://github.com/ScruffyTheMoose/blockChain/blob/main/imgs/Node%20Manager.PNG)

## Endpoints
At the moment, over a dozen endpoints exist for controlling node operations and interactions. Some of these endpoints exist strictly for automated calls between nodes. I will list the useable endpoints below, but I encourage reading through the code to better understand how each endpoint works and the structure of responses.

#### GET Requests
- Mining a new block:
  - /mine
 
- Get the node's ID:
  - /id

- Get the node's transaction registry:
  - /transactions

- Get the node's current blockchain:
  - /chain

- Get the node's node registry:
  - /nodes

- Resolves the network using the consensus algorithm:
  - /resolve

- Get the node's current holdings and node registry:
  - /status

#### POST Requests
- Create a new transaction:
  - /transactions/new

- Registers a new node:
  - /nodes/register

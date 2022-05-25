![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)

`CRAPchain` is a private blockchain built from scratch purely to learn about this popular (and useless) decentralized network technology. Through a dynamic network of nodes, CRAPchain can facilitate transactions and mint new blocks all while maintaining consensus. All operations on the network are validated using unique node IDs and a proofing algorithm.

At the moment, 13 endpoints exist for controlling node operations -
```
/mine
```
GET - This mode mines a new block

```
/id
```
GET - Returns the ID of this node

```
/transactions
```
GET - Returns the current registry of transactions on this node

```
/transactions/new
```
POST - Generates a new transaction and adds it to the registry on this node

```
/transactions/_cleanup
```
GET - To be called while resolving the network

```
/chain
```
GET - Returns the chain on this node

```
/chain/replace
```
POST - Validates the given chain and replaces obsolete chain on this node

```
/nodes
```
GET - Returns the registry of nodes on this node

```
/nodes/replace
```
POST - Pushing new nodes to the node registry on this node

```
/nodes/register
```
POST - Cross registers this node and the given node

```
/nodes/_response_register
```
POST - To be when registering a new node

```
/resolve
```
GET - Resolves all nodes across the network, ensuring every node has the authoritative chain and node registry while also removing old transactions

```
/status
```
GET - Returns the current connections and known holdings of this node

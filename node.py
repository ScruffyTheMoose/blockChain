from chain import Blockchain
from uuid import uuid4
import requests
import sys

from flask import Flask, jsonify, request


# instantiating flask node
app = Flask(__name__)

# unique address for this node
node_id = str(uuid4()).replace("-", "")

# instantiate blockchain
blockchain = Blockchain(node_id)


@app.route("/mine", methods=["GET"])
def mine():
    """[GET] - Mines a new Block"""

    # getting info from the last Block
    prevBlock = blockchain.tail
    prevProof = prevBlock["proof"]

    # finding proof key for Block being mined
    proof = blockchain.pow(prevProof)

    # awarding one unit for successfully mined Block
    blockchain.newTrans(sender="0", recipient=node_id, amount=1)

    # updating this node registry to be able to collect all transactions across the network
    blockchain.nodeConsensus()

    # collecting all transactions
    for node in list(blockchain.nodes):
        data = requests.get(f"{node}/transactions")

        # appending other transactions to this nodes
        if data.status_code == 200:

            # merging the two dictionaries
            blockchain.transactions = {
                **blockchain.transactions,
                **data.json()["transactions"],
            }

    # creating the new Block and adding it to the chain
    prevHash = blockchain.hash(prevBlock)
    block = blockchain.newBlock(proof, prevHash)

    # now that new block has been added to chain, we resolve the network
    requests.get(f"{request.url_root}/resolve")

    # response to be passed back to node
    response = {
        "message": "New Block forged",
        "index": block["index"],
        "transactions": block["transactions"],
        "proof": proof,
        "prev_hash": block["prev_hash"],
    }

    return jsonify(response), 200


@app.route("/id", methods=["GET"])
def getID():
    """[GET] - Returns this nodes unique ID"""

    response = {"id": blockchain.id}

    return jsonify(response), 200


@app.route("/transactions", methods=["GET"])
def getTrans():
    """[GET] - Produce the transaction list on this node"""

    response = {
        "transactions": blockchain.transactions,
        "length": len(blockchain.transactions),
    }

    return jsonify(response), 200


@app.route("/transactions/new", methods=["POST"])
def newTrans():
    """[POST] - Creates a new transaction on the current Block"""

    # getting the JSON object that was pushed
    args = request.get_json()
    reqs = ["sender", "recipient", "amount"]

    # verifying required 3 arguments were given
    if not all(k in args for k in reqs):
        return "Missing arguments", 400

    if args["sender"] != blockchain.id:
        return "Sender address does not match this node", 400

    # creating new transaction which returns the index of the block where the transaction will be stored
    idx = blockchain.newTrans(
        sender=args["sender"],
        recipient=args["recipient"],
        amount=args["amount"],
    )

    response = {"message": f"Transaction will be added to Block {idx}"}
    return jsonify(response), 201


@app.route("/transactions/_cleanup", methods=["GET"])
def cleanTrans():
    """[GET] - Checks the chain and removes any redundant transactions from this nodes list"""

    removed = list()

    # checking each block
    for block in blockchain.chain:

        # checking each transaction in this node
        for id in blockchain.transactions.keys():

            # checking transaction IDs from this node against the authoritative chain
            # removing any transactions with IDs already in a block
            if id in block["transactions"]:
                removed.append(blockchain.transactions.pop(id))

    if removed:
        response = {
            "message": "Some transactions were removed from this node",
            "removed": removed,
        }
    else:
        response = {
            "message": "No transactions were removed from this node",
        }

    return jsonify(response), 200


@app.route("/chain", methods=["GET"])
def getChain():
    """[GET] - Produces the entire chain on this node"""

    response = {
        "chain": blockchain.chain,
        "length": len(blockchain.chain),
    }

    return jsonify(response), 200


@app.route("/chain/replace", methods=["POST"])
def replaceChain():
    """[POST] - Replaces the chain on this node with the authoritative chain"""

    newChain = request.get_json()["chain"]

    verify = blockchain.verifyChain(newChain)

    if verify:
        blockchain.chain = newChain

        response = {
            "message": "The chain on this node was replaced with the authoritative chain",
            "chain": blockchain.chain,
        }
    else:
        response = {
            "message": "The submitted chain was failed verification and was rejected",
            "chain": blockchain.chain,
        }

    return jsonify(response), 201


@app.route("/nodes", methods=["GET"])
def getNodes():
    """[GET] - Produce the node registry on this node"""

    response = {
        "nodes": list(blockchain.nodes),
        "length": len(blockchain.nodes),
    }

    return jsonify(response), 200


@app.route("/nodes/replace", methods=["POST"])
def replaceNodes():
    """[POST] - Replaces the node registry on this node with the authoritative registry"""

    newRegistry = request.get_json()["nodes"]

    for node in newRegistry:
        blockchain.registerNode(node)

    response = {
        "message": "Node registry has been updated!",
        "nodes": list(blockchain.nodes),
    }

    return jsonify(response), 201


@app.route("/nodes/register", methods=["POST"])
def registerNodes():
    """[POST] - Register a new node on the chain"""

    nodes = request.get_json()["nodes"]
    initNodes = blockchain.nodes
    failed = list()

    # data to be posted to other nodes for cross registration
    thisNode = request.url_root
    submission = {
        "nodes": [f"{thisNode}"],
    }

    if not nodes or nodes is None:
        return "Error: Please supply a valid list of Nodes", 400

    for node in nodes:
        registration = blockchain.registerNode(node)

        # checking that address was valid
        if not registration:
            failed.append(node)
        else:
            # cross registering
            requests.post(f"{node}/nodes/_response_register", json=submission)

    if failed:
        # there were errors, resetting registry to initial
        blockchain.nodes = initNodes

        response = {
            "message": "There were errors during registration with some nodes, the registry was not changed",
            "errors": failed,
            "nodes": list(blockchain.nodes),
        }

    else:
        response = {
            "message": "New nodes have been registered",
            "nodes": list(blockchain.nodes),
        }

    return jsonify(response), 201


@app.route("/nodes/_response_register", methods=["POST"])
def responseRegister():
    """[POST] - Endpoint for cross registering with a newly registered node

    Ex: Node-A registers on Node-B. This endpoint will be called by Node-B automatically to register itself on Node-A.
    This will ensure double-linkage across the chain.
    """

    nodes = request.get_json()["nodes"]

    if not nodes or nodes is None:
        return "Error: Please supply a valid list of Nodes", 400

    blockchain.registerNode(nodes[0])

    response = {
        "message": "New nodes have been registered",
        "nodes": list(blockchain.nodes),
    }

    return jsonify(response), 201


@app.route("/resolve", methods=["GET"])
def consensus():
    """[GET] - Resolves any existing conflicts and ensures consensus on this node with the network"""

    # checks that the node registry is up-to-date
    # when nodeConsensus() completes, this node will have the authoritative registry
    nodeStat = blockchain.nodeConsensus()
    # then checks all nodes for most current chain
    chainStat = blockchain.chainConsensus()

    # authoritative list of node registry to be sent to all other nodes
    nodeObj = {"nodes": list(blockchain.nodes)}

    # authoritative chain to be sent to all other nodes
    chainObj = {"chain": blockchain.chain}

    # sending authoritative node registry and chain to all other node endpoints
    for node in list(blockchain.nodes):
        requests.post(f"{node}/nodes/replace", json=nodeObj)
        requests.post(f"{node}/chain/replace", json=chainObj)
        requests.get(f"{node}/transactions/_cleanup")

    if chainStat:
        response = {"message": "Our chain was replaced", "chain": blockchain.chain}
    else:
        response = {"message": "Our chain is authoritative", "chain": blockchain.chain}

    if nodeStat:
        response["message"] += " - Our node registry was updated"
        response["nodes"] = list(blockchain.nodes)
    else:
        response["message"] += " - Our node registry is authorititive"
        response["nodes"] = list(blockchain.nodes)

    return jsonify(response), 200


@app.route("/status", methods=["GET"])
def status():
    """[GET] - Produces all connections and account associated holdings"""

    # ISSUE: This will pull the current status, but if the node doesn't have access to authoritative chain, the holdings are incorrect
    # SOLUTION: Chain consensus is required for status (/resolve endpoint)
    # ACTION: We will leave it broken for now to see what types of disconnects develop across the network

    amount = 0

    # checking all the blocks
    for block in blockchain.chain:
        for transaction in block["transactions"].values():
            if transaction["sender"] == blockchain.id:
                amount -= transaction["amount"]

            if transaction["recipient"] == blockchain.id:
                amount += transaction["amount"]

    # checking currently tracked transactions
    for transaction in blockchain.transactions.values():
        if transaction["sender"] == blockchain.id:
            amount -= transaction["amount"]

        if transaction["recipient"] == blockchain.id:
            amount += transaction["amount"]

    response = {
        "connections": list(blockchain.nodes),
        "holdings": amount,
    }

    return jsonify(response), 200


if __name__ == "__main__":
    portNum = sys.argv[1]
    app.run(host="127.0.0.1", port=portNum)

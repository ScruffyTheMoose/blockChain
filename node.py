import this
from chain import Blockchain
from uuid import uuid4
from urllib.parse import urlparse
import requests
import json
import sys

from flask import Flask, jsonify, request

# instantiating flask node
app = Flask(__name__)

# unique address for this node
node_id = str(uuid4()).replace("-", "")

# instantiate blockchain
blockchain = Blockchain()


@app.route("/mine", methods=["GET"])
def mine():
    """[GET] - Mines a new Block"""

    # getting info from the last Block
    prevBlock = blockchain.tail
    prevProof = prevBlock["proof"]

    # finding proof key for Block being mined
    proof = blockchain.pow(prevProof)

    # awarding one unit for successfully mined Block
    blockchain.newTrans(
        sender="0",
        recipient=node_id,
        amount=1,
    )

    # creating the new Block and adding it to the chain
    prevHash = blockchain.hash(prevBlock)
    block = blockchain.newBlock(proof, prevHash)

    # response to be passed back to node
    response = {
        "message": "New Block forged",
        "index": block["index"],
        "transactions": block["transactions"],
        "proof": proof,
        "prev_hash": block["prev_hash"],
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

    # creating new transaction which returns the index of the block where the transaction will be stored
    idx = blockchain.newTrans(
        sender=args["sender"],
        recipient=args["recipient"],
        amount=args["amount"],
    )

    response = {"message": f"Transaction will be added to Block {idx}"}
    return jsonify(response), 201


@app.route("/chain", methods=["GET"])
def getChain():
    """[GET] - Produces the entire chain"""

    response = {
        "chain": blockchain.chain,
        "length": len(blockchain.chain),
    }

    return jsonify(response), 200


@app.route("/nodes", methods=["GET"])
def getNodes():
    """[GET] - Produce a node's registry of nodes"""

    response = {
        "nodes": list(blockchain.nodes),
        "length": len(blockchain.nodes),
    }

    return jsonify(response), 200


@app.route("/nodes/register", methods=["POST"])
def registerNodes():
    """[POST] - Register a new node on the chain"""

    nodes = request.get_json()["nodes"]
    initNodes = blockchain.nodes
    failed = list()

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
            requests.post(f"{node}/nodes/response_register", json=submission)

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


@app.route("/nodes/response_register", methods=["POST"])
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
    """[GET] - Resolves any existing conflicts and ensures consensus across the chain"""

    nodeStat = blockchain.nodeConsensus()
    chainStat = blockchain.chainConsensus()

    if chainStat:
        response = {"message": "Our chain was replaced", "chain": blockchain.chain}
    else:
        response = {"message": "Our chain is authoritative", "chain": blockchain.chain}

    if nodeStat:
        response["message"] += " - Our node registry was updated"
        response["nodes"] = list(blockchain.nodes)
    else:
        response["message"] += " - Our node registry is authoratitive"
        response["nodes"] = list(blockchain.nodes)

    return jsonify(response), 200


if __name__ == "__main__":
    portNum = sys.argv[1]
    app.run(host="127.0.0.1", port=portNum)

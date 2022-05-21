import hashlib
import time
import json
import requests
from urllib.parse import urlparse


class Blockchain:

    def __init__(self) -> None:
        self.chain = list()
        self.transactions = list()
        self.nodes = set()

        # genesis block
        self.newBlock(proof=100, prevHash=1)

    def newBlock(self, proof, prevHash) -> dict:
        block = {
            "index": len(self.chain) + 1,
            "timestamp": time.time(),
            "transactions": self.transactions,
            "proof": proof,
            "prev_hash": prevHash,
        }

        # adding block to chain
        self.chain.append(block)

        # clearing transaction list
        self.transactions = list()

        # returning reference to block
        return block

    def newTrans(self, sender, recipient, amount) -> int:
        self.transactions.append({
            "sender": sender,
            "recipient": recipient,
            "amoumnt": amount,
        })

        # returning index of block where this transaction will be stored
        return self.tail["index"] + 1

    @staticmethod
    def hash(block) -> str:
        # convert block into JSON formatted string with UTF-8 encoding
        blockString = json.dumps(block, sort_keys=True).encode()

        # 256 bit hash of blockString digested into string format
        hashedBlock = hashlib.sha256(blockString).hexdigest()

        return hashedBlock

    @property
    def tail(self) -> dict:
        return self.chain[-1]

    def pow(self, lastProof):
        # attempt key
        proof = 0

        # iteratively test to see if hash pattern is met
        while self.verifyProof(lastProof, proof) is False:
            proof += 1

        # returning successful proof key
        return proof

    @staticmethod
    def verifyProof(lastProof, proof):
        attempt = f"{lastProof}{proof}".encode()
        hashed = hashlib.sha256(attempt).hexdigest()

        # good proof key produced hash with 4 leading zeros
        return hashed[:4] == "0000"

    def registerNode(self, address):
        parsedURL = urlparse(address)
        self.nodes.add(parsedURL.netloc)

    def verifyChain(self, chain):
        prevBlock = chain[0]
        currentIdx = 1

        while currentIdx < len(chain):
            block = chain[currentIdx]

            # validating blocks are hashed and ordered correctly
            if block['prev_hash'] != self.hash(prevBlock):
                return False

            if not self.verifyProof(prevBlock['proof'], block['proof']):
                return False

            prevBlock = block
            currentIdx += 1

        return True

    def resolveConflicts(self):
        neighbors = self.nodes
        newChain = None

        # length of our chain
        maxLength = len(self.chain)

        for node in neighbors:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > maxLength and self.verifyChain(chain):
                    maxLength = length
                    newChain = chain

        if newChain:
            self.chain = newChain
            return True

        return False
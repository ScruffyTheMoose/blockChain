import hashlib
import time
import json


class Blockchain:

    def __init__(self) -> None:
        self.chain = list()
        self.transactions = list()

        # genesis block
        self.newBlock(proof=100, prevHash=1)

    def newBlock(self, proof, prevHash) -> dict:
        block = {
            "index": len(self.chain) + 1,
            "timestamp": time.time(),
            "transactions": list(),
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

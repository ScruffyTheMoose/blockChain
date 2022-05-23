import hashlib
import time
import json
import requests
from urllib.parse import urlparse


# TBD
# Each node needs to have an actual wallet for tracking all sent/recieved units

# Each node's UUID needs to be tracked alongside the nodes address so when a transaction is registered, all the nodes can read
# the transaction and be updated accordingly

# Transaction validation needs to be built


class Blockchain:
    def __init__(self) -> None:
        self.chain = list()
        self.transactions = list()
        self.nodes = set()

        # genesis block
        self.newBlock(proof=100, prevHash=1)

    def newBlock(self, proof, prevHash) -> dict:
        """Constructs a new Block

        Args:
            proof (int): Proof key used for the hash
            prevHash (str): Hash of previous Block for verification

        Returns:
            dict: The data being stored in the Block
        """

        block = {
            "index": len(self.chain) + 1,
            "time": time.time(),
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
        """Create a new transaction for the current Block

        Args:
            sender (str): Node address of sender
            recipient (str): Node address of recipient
            amount (int): Quantity of units being sent

        Returns:
            int: Index of the Block where this transaction will be stored
        """

        self.transactions.append(
            {
                "sender": sender,
                "recipient": recipient,
                "amoumnt": amount,
                "time": time.time(),
            }
        )

        # returning index of block where this transaction will be stored
        return self.tail["index"] + 1

    @staticmethod
    def hash(block) -> str:
        """To hash a Block

        Args:
            block (dict): The Block that will be hashed

        Returns:
            str: Resulting hash
        """

        # convert block into JSON formatted string with UTF-8 encoding
        blockString = json.dumps(block, sort_keys=True).encode()

        # 256 bit hash of blockString digested into string format
        hashedBlock = hashlib.sha256(blockString).hexdigest()

        return hashedBlock

    @property
    def tail(self) -> dict:
        """The last Block in the chain

        Returns:
            dict: The data stored in the last Block
        """

        return self.chain[-1]

    def pow(self, lastProof) -> int:
        """Proof of Work to identify the correct proof key for a Block
        In this case, want to find a new proof key such that when concatenated with the previous
        proof key, the new hash has three leading zeros.

        Args:
            lastProof (int): The previous Block's proof key

        Returns:
            int: New proof key
        """

        # attempt key
        proof = 0

        # iteratively test to see if hash pattern is met
        while self.verifyProof(lastProof, proof) is False:
            proof += 1

        # returning successful proof key
        return proof

    @staticmethod
    def verifyProof(lastProof, proof) -> bool:
        """Verifies that the given proof key is valid.

        Args:
            lastProof (int): Previous Block's proof key
            proof (int): Current proof key attempt

        Returns:
            bool: True when proof key is valid, else False
        """

        attempt = f"{lastProof}{proof}".encode()
        hashed = hashlib.sha256(attempt).hexdigest()

        # good proof key produced hash with 4 leading zeros
        return hashed[:4] == "0000"

    def registerNode(self, address) -> bool:
        """Registers a new node on the chain

        Args:
            address (str): The network address of the new node
        """

        parsedURL = "http://" + urlparse(address).netloc

        # checking that URL was not reduced to empty string
        if parsedURL:
            self.nodes.add(parsedURL)
            return True

        return False

    def verifyChain(self, chain) -> bool:
        """Verifies that the current chain is valid by checking all hashes and proof keys are valid

        Args:
            chain (list): The entire stored Blockchain on this node

        Returns:
            bool: True if chain is valid, else False
        """

        prevBlock = chain[0]
        currentIdx = 1

        while currentIdx < len(chain):
            block = chain[currentIdx]

            # validating blocks are hashed and ordered correctly
            if block["prev_hash"] != self.hash(prevBlock):
                return False

            if not self.verifyProof(prevBlock["proof"], block["proof"]):
                return False

            prevBlock = block
            currentIdx += 1

        return True

    # must also verify that all nodes share identical node lists
    # resolving conflicts should be called for all nodes when any node builds a new block or a new node is added
    # this would ensure there are never conflicts between two different chains
    def chainConsensus(self) -> bool:
        """Resolves all conflicts across the network to ensure consensus of chain data

        Returns:
            bool: True if conflicts existed and were resolved, else False for no changes made
        """

        neighbors = self.nodes
        newChain = None

        # length of our chain
        currentLength = len(self.chain)

        for node in neighbors:
            # request to node for its chain
            response = requests.get(f"{node}/chain")

            if response.status_code == 200:
                length = response.json()["length"]
                chain = response.json()["chain"]

                if length > currentLength and self.verifyChain(chain):
                    currentLength = length
                    newChain = chain

        if newChain:
            self.chain = newChain
            return True

        return False

    def nodeConsensus(self) -> bool:
        """Checks that node registry is up-to-date

        Returns:
            bool: True if update was done, else False for no changes made
        """

        children = self.nodes
        initLength = len(self.nodes)

        for node in children:
            # request to node for its registered nodes
            response = requests.get(f"{node}/nodes")

            if response.status_code == 200:
                # joining both sets, any new nodes will be added
                otherNodes = response.json()["nodes"]
                self.nodes = self.nodes.union(otherNodes)

        if len(self.nodes) > initLength:
            self.nodeConsensus()  # calls recursively until length is static
            return True

        return False

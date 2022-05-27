import requests
import hashlib
import json


class Observer:
    def __init__(self, firstNode: str) -> None:
        """Constructor for the observer node
        This object will serve as the intermediary between the GUI and all the nodes on the blockchain

        Args:
            firstNode (str): URL root for any individual node already on the network
        """

        self.nodes = set([firstNode])
        self.chain = list()

        # building node registry
        self.updateNodes()
        # grabbing authoritative chain
        self.updateChain()

        self.nodeData = dict()
        self.updateData()

    def updateNodes(self) -> bool:
        """Recursively builds the complete node registry and stores it on this instance

        Returns:
            bool: Returns True if node registry was updated, else False
        """

        # our known nodes on the network
        registry = self.nodes
        # the initial size of the registry
        initLength = len(self.nodes)

        for node in registry:
            # request to node for its registered nodes
            response = requests.get(f"{node}/nodes")

            if response.status_code == 200:
                # joining both sets, any new nodes will be added
                otherNodes = response.json()["nodes"]
                self.nodes = self.nodes.union(otherNodes)

        if len(self.nodes) > initLength:
            self.updateNodes()  # calls recursively until length is static
            return True

        return False

    def updateChain(self) -> bool:
        """Resolves all conflicts across the network to ensure consensus of chain data

        Returns:
            bool: True if conflicts existed and were resolved, else False for no changes made
        """

        registry = self.nodes
        newChain = None

        # length of our chain
        initLength = len(self.chain)

        for node in registry:
            # request to node for its chain
            response = requests.get(f"{node}/chain")

            if response.status_code == 200:
                length = response.json()["length"]
                chain = response.json()["chain"]

                if length > initLength and self.verifyChain(chain):
                    initLength = length
                    newChain = chain

        if newChain:
            self.chain = newChain
            return True

        return False

    def updateData(self) -> None:
        """Pulls all needed data from nodes across the network to track their status"""

        results = dict()

        for node in self.nodes:
            # getting chain and node registry from other nodes
            newChain = requests.get(f"{node}/chain")["chain"]
            newRegistry = requests.get(f"{node}/nodes")["nodes"]

            results[node] = {
                "nodes": newRegistry,
                "chain": newChain,
            }

        self.nodeData = results

    def verifyChain(self, chain: list) -> bool:
        """Verifies that the given chain is valid by checking all hashes and proof keys are valid and in-order

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

    @staticmethod
    def verifyProof(lastProof: str, proof: str) -> bool:
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

    @staticmethod
    def hash(block: dict) -> str:
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

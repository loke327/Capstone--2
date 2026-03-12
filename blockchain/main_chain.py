from datetime import datetime
from blockchain.utils import sha256_hash

class MainChain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        block = {
            "index": 0,
            "timestamp": str(datetime.utcnow()),
            "sidechain_id": "GENESIS",
            "sidechain_hash": "0",
            "previous_hash": "0"
        }
        block["block_hash"] = sha256_hash(block)
        self.chain.append(block)

    def anchor_sidechain(self, sidechain_id, sidechain_hash):
        prev_block = self.chain[-1]

        block = {
            "index": len(self.chain),
            "timestamp": str(datetime.utcnow()),
            "sidechain_id": sidechain_id,
            "sidechain_hash": sidechain_hash,
            "previous_hash": prev_block["block_hash"]
        }

        block["block_hash"] = sha256_hash(block)
        self.chain.append(block)

        return block

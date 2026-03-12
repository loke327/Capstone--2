from datetime import datetime
from blockchain.utils import sha256_hash

class Sidechain:
    def __init__(self, chain_id):
        self.chain_id = chain_id
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        block = {
            "index": 0,
            "timestamp": str(datetime.utcnow()),
            "data_hash": "GENESIS",
            "previous_hash": "0"
        }
        block["block_hash"] = sha256_hash(block)
        self.chain.append(block)

    def add_block(self, data_hash):
        prev_block = self.chain[-1]

        block = {
            "index": len(self.chain),
            "timestamp": str(datetime.utcnow()),
            "data_hash": data_hash,
            "previous_hash": prev_block["block_hash"]
        }

        block["block_hash"] = sha256_hash(block)
        self.chain.append(block)

        return block

    def latest_hash(self):
        return self.chain[-1]["block_hash"]

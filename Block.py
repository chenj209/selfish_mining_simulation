class Block:
    def __init__(self, id, miner_id, timestamp, parent_id, height):
        """
        Represent a block in the blockchain
        Args:
            id: block id
            miner: Miner id
            timestamp: Clock counter
            parent: parent id
        """
        self.id = id
        self.miner = miner_id
        self.timestamp = timestamp
        self.parent = parent_id
        self.children = [] # ids of children
        self.height = height
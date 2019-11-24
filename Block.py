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
        self.miner_id = miner_id
        self.timestamp = timestamp
        self.parent_id = parent_id
        self.children = [] # ids of children
        self.height = height

    def subtree_str(self, blocks, level=0):
        ret = "\t" * level + f"<{self.id},{self.miner_id}>" + "\n"
        children_str = [blocks[child].subtree_str(blocks, level + 1) for child in self.children]
        children_str.sort(key=lambda s: len(s))
        ret += "".join(children_str)
        # for child in self.children:
        #     ret += blocks[child].subtree_str(blocks, level + 1)
        return ret






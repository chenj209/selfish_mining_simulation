class Block:
    def __init__(self, id, miner_id, timestamp, parent_id, height, uncle_ids=[]):
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
        # self.other_children = [] # invalid childrens
        self.uncles = uncle_ids # ids of uncles
        self.height = height
        self.notified_miner_count = 0
        self.pending_notified_miner_count = 1 # for the miner who mined the block
        self.racing = False
        self.win_race_count = 0
        self.notified_miners = []

    def need_more_uncles(self):
        return len(self.uncles) < 2


    def add_child(self, child_id):
        self.children.append(child_id)
        '''
        # currently assumes only first three children is valid
        if len(self.children) < 3:
            self.children.append(child_id)
        else:
            self.other_children.append(child_id)
        '''

    def __str__(self):
        return f"ID:{self.id}\nMID:{self.miner_id}\nPR:{self.notified_miner_count}\nPPR:{self.pending_notified_miner_count}\n"


    def subtree_str(self, blocks, level=0):
        ret = "\t" * level + f"<{self.id},{self.miner_id},{self.notified_miner_count},{self.pending_notified_miner_count}>" + "\n"
        children_str = [blocks[child].subtree_str(blocks, level + 1) for child in self.children]
        children_str.sort(key=lambda s: len(s))
        ret += "".join(children_str)
        # for child in self.children:
        #     ret += blocks[child].subtree_str(blocks, level + 1)
        return ret

    # def subtree_str2(self, blocks, level=0):
    #     ret = f"<{'{0:0=4d}'.format(self.id)},{'{0:0=4d}'.format(self.miner_id)}> | "
    #     placeholder = " " * 14
    #     children_str_tokens = []
    #     children_str = [blocks[child].subtree_str2(blocks, level + 1) for child in self.children]
    #     children_str.sort(key=lambda s: s.count("\n"), reverse=True)
    #     for child_str in children_str:
    #         ret += placeholder
    #         tokens = child_str.strip("\n").split("\n")
    #         i = 0
    #         while i < min(len(children_str_tokens), len(tokens)):
    #             children_str_tokens[i] += tokens[i]
    #             i += 1
    #         if i < len(tokens):
    #             children_str_tokens.extend(tokens[i:])
    #     ret = ret[:-1] + "|"
    #     return ret + "\n" + "\n".join(children_str_tokens)
    #







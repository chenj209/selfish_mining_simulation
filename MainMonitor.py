import random
from enum import IntEnum


# def get_longest_chain(prime_block, blocks):
#     """
#     Perform a BFS to return the block heads of the longest chain, sorted in timestamp order
#     Args:
#         prime_block: the first block of blockchain
#         blocks: dict(block_id, block)
#
#     Returns:
#         [Block], block heads of longest chain, sorted in timestamp order
#     """
#     queue = [prime_block]
#     while len(queue[0].children) == 0:
#         current = queue.pop(0)
#         for child in current.children:
#             queue.append(blocks[child])


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

class EventType(IntEnum):
    ANY = 0
    NEW_BLOCK = 1


class Event:
    def __init__(self, timestamp):
        self.timestamp = timestamp

    def process(self, miner):
        pass

class NewBlockEvent(Event):
    def __init__(self, timestamp, block):
        super().__init__(timestamp)
        self.block = block
        self.type = EventType.NEW_BLOCK

    def process(self, miner):
        if miner.update_blockchain(self.block):
            miner.notify_neighbours(self.block)


class Miner:
    def __init__(self, id, pow, delay, bandwidth):
        self.clock = 0
        self.id = id
        self.pow = pow
        self.delay = delay
        self.bandwidth = bandwidth
        self.future_events = []
        self.neighbours = []
        self.blocks = {}
        self.longest_chain_heads = [] # priority queue of longest chain heads

    def mine(self):
        block_head = self.longest_chain_heads[0]
        nounce =  self.pow.try_POW()
        if nounce:
            new_block =  Block(self.pow.block_count, self.id, block_head.id, self.clock, block_head.height+1)
            block_head.children.append(new_block)

    def update_event(self, new_event):
        if len(self.future_events) == 0:
            self.future_events.append(new_event)
        else:
            for i in range(len(self.future_events)):
                event = self.future_events[i]
                if new_event.timestamp > event:
                    self.future_events.insert(new_event, i+1)


    def update_blockchain(self, block):
        if block.id not in self.blocks:
            self.blocks[block.id] = block
            return True
        if block.miner != self.blocks[block.id]:
            print(f"Block conflict")

        return False

    def notify_neighbours(self, block):
        new_event = NewBlockEvent(self.clock+self.delay, block)
        for neighbour in self.neighbours:
            neighbour.update_event(new_event)


    def run(self):
        while len(self.future_events) > 0 and self.future_events[0].timestamp >= self.clock:
            self.future_events[0].process(self)
        new_block = self.mine()
        if new_block:
            self.notify_neighbours(new_block)

class NetworkGraphGen:
    @staticmethod
    def random_graph(miners, neighbour_count):
        for i in range(len(miners)):
            miners[i].neighbours = random.sample(miners[:i] + miners[i+1:], neighbour_count)





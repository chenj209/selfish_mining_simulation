from Block import Block
from Event import NewBlockEvent


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
            new_block =  Block(self.pow.block_count, self.id, block_head.id, self.clock, block_head.height + 1)
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
        new_event = NewBlockEvent(self.clock + self.delay, block)
        for neighbour in self.neighbours:
            neighbour.update_event(new_event)


    def run(self):
        while len(self.future_events) > 0 and self.future_events[0].timestamp >= self.clock:
            self.future_events[0].process(self)
        new_block = self.mine()
        if new_block:
            self.notify_neighbours(new_block)
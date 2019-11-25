from Block import Block
from Event import SendNewBlockEvent, process_event


class Miner:
    def __init__(self, id, pow, delay, bandwidth, hash_power=1):
        self.clock = 0
        self.upload_bandwidth = bandwidth
        self.download_bandwidth = bandwidth
        self.hash_power = hash_power
        self.id = id
        self.pow = pow
        self.delay = delay
        self.bandwidth = bandwidth
        self.recv_events = [] # future events to process
        self.send_events = [] # events that need to be sent to neighbours
        self.neighbours = []
        self.blocks = {}
        self.notified_blocks = []
        self.longest_chain_heads = [pow.prime_block] # priority queue of longest chain heads

    def mine(self):
        block_head = self.longest_chain_heads[0]
        nounce =  self.pow.try_POW()
        if nounce:
            new_block =  Block(self.pow.block_count, self.id, self.clock, block_head.id, block_head.height + 1)
            block_head.children.append(new_block.id)
            return new_block

    # @staticmethod
    # def update_event(new_event, events):
    #     if len(events) == 0:
    #         events.append(new_event)
    #     else:
    #         for i in range(len(events)):
    #             event = events[i]
    #             if new_event.timestamp > event.timestamp:
    #                 events.insert(new_event, i+1)


    def update_blockchain(self, block):
        if block.id not in self.blocks:
            self.blocks[block.id] = block
            if block.height > self.longest_chain_heads[0].height:
                self.longest_chain_heads = [block]
            elif block.height == self.longest_chain_heads:
                self.longest_chain_heads.append(block)
            return True
        if block.miner_id != self.blocks[block.id].miner_id:
            print(f"Block conflict: {block} vs. {self.blocks[block.id]}")

        return False

    def notify_neighbours(self, block):
        for neighbour in self.neighbours:
            new_event = SendNewBlockEvent(self.clock, block, neighbour)
            self.send_events.append(new_event)

    # def process_event(self, events, bandwidth):
    #     current_bandwidth = bandwidth
    #     while len(events) > 0 \
    #             and events[0].timestamp >= self.clock \
    #             and current_bandwidth > 0:
    #         current_event = events.pop(0)
    #         current_event.process(self)
    #         current_bandwidth -= 1

    def run(self):
        # download_bandwidth = self.download_bandwidth
        # upload_bandwidth = self.upload_bandwidth
        # while len(self.recv_events) > 0 \
        #         and self.recv_events[0].timestamp >= self.clock \
        #         and download_bandwidth > 0:
        #     current_event = self.recv_events.pop(0)
        #     current_event.process(self)
        #     download_bandwidth -= 1

        process_event(self, self.recv_events, self.download_bandwidth)

        new_blocks = []
        for i in range(self.hash_power):
            new_block = self.mine()
            if new_block:
                self.notify_neighbours(new_block)
                new_blocks.append(new_block)

        process_event(self, self.send_events, self.upload_bandwidth)

        return new_blocks
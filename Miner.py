from Block import Block
from Event import SendNewBlockEvent, process_event
import random


class Miner:
    def __init__(self, id, pow, delay, bandwidth, hash_power=1):
        self.clock = 0
        # clock time of simulation
        self.upload_bandwidth = bandwidth
        # number of update events that can be processed in 1 timestamp
        self.download_bandwidth = bandwidth
        # number of download events that can be processed in 1 timestamp
        self.hash_power = hash_power
        # number of pow attempts per timestamp
        self.id = id
        # id of miner
        self.pow = pow
        # pow that is shared among all miners
        self.delay = delay
        # number of timestamp added to upload event timestamp when sent
        self.recv_events = {}
        # dictionary of future events to process, using timestamp as key
        self.send_events = {}
        # dictionary of events that need to be sent to neighbours, using timestamp as key
        self.neighbours = []
        # Miner object of neighbours of this miner
        self.blocks = {}
        # dict{block_id: block object}, received blocks
        self.longest_chain_heads = [pow.prime_block]
        # priority queue of longest chain heads, currently managed using timestamp

    def mine(self):
        """
        Mine pow 1 time, create a new block if mined successfully
        Returns:
            new_block: Block object
        """
        block_head = self.longest_chain_heads[0]
        nounce =  self.pow.try_POW()
        if nounce:
            new_block =  Block(self.pow.block_count-1, self.id, self.clock, block_head.id, block_head.height + 1)
            block_head.add_child(new_block.id)
            self.blocks[new_block.id] = new_block
            return new_block


    def update_blockchain(self, block):
        """
        update self.blocks and self.longest_chain_heads with block.
        Args:
            block: received block

        Returns:
            Bool: return true if the block is new
        """
        if block.id not in self.blocks:
            self.blocks[block.id] = block
            block.notified_miner_count += 1
            if block.height > self.longest_chain_heads[0].height:
                self.longest_chain_heads = [block]
            elif block.height == self.longest_chain_heads:
                self.longest_chain_heads.append(block)
            return True
        if block.miner_id != self.blocks[block.id].miner_id:
            print(f"Block conflict: {block} vs. {self.blocks[block.id]}")

        return False

    def notify_neighbours(self, block):
        """
        Notify all neighbours about block by creating SendNewBlockEvent and add that event to
        self.send_events (self.send_events will be processed at the end of this timestamp)
        Args:
            block: Block object to notify
        """
        random.shuffle(self.neighbours)
        for neighbour in self.neighbours:
            new_event = SendNewBlockEvent(self.clock, block, neighbour)
            if new_event.timestamp not in self.send_events:
                self.send_events[new_event.timestamp] = []
            self.send_events[new_event.timestamp].append(new_event)

    def run(self):
        """
        Run simulation for 1 timestamp.
        This includes:
            1. process recevied events up to download bandwidth times
            2. mine self.hash_power times, call notify neighbours if needed
            3. process sent events up to upload bandwidth times
        Returns:
            new_blocks: return any new blocks mined to MainMonitor
        """

        # process each received events that is greater than current clock time
        # up to self.download_bandwidth times, unprocessed events will be processed
        # in next timestamp
        # if len(self.recv_events) > 0:
        #     print("wtf")
        process_event(self, self.recv_events, self.download_bandwidth)

        new_blocks = []
        for i in range(self.hash_power):
            new_block = self.mine()
            if new_block:
                self.notify_neighbours(new_block)
                new_blocks.append(new_block)

        # process each send events that is greater than current clock time
        # up to self.upload_bandwidth times, unprocessed events will be processed
        # in next timestamp
        # if len(self.send_events) > 0:
            # print("wtf")
        process_event(self, self.send_events, self.upload_bandwidth)
        self.clock += 1

        return new_blocks

class SelfishMiner(Miner):
    def __init__(self, id, pow, delay, bandwidth, hash_power=1):
        super().__init__(id, pow, delay, bandwidth, hash_power)
        self.private_chain_head = None
        # head of private chain that is currently worked on

    def notify_neighbours(self, block):
        """
        Notify neighbours according to selfish strategy
        """
        pass

    def update_blockchain(self, block):
        """
        Update private chain or publish private chain according to what received
        """
        pass






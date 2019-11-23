from enum import IntEnum


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
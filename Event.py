from enum import IntEnum


class EventType(IntEnum):
    ANY = 0
    RECV_NEW_BLOCK = 1
    SEND_NEW_BLOCK = 2

class Event:
    def __init__(self, timestamp):
        self.timestamp = timestamp

    def process(self, miner):
        pass

def update_event(new_event, events):
    # if len(events) == 0:
    events.append(new_event)
    # else:
    #     for i in range(len(events)):
    #         event = events[len(events) - i - 1]
    #         if new_event.timestamp > event.timestamp:
    #             events.insert(i+1, new_event)

def process_event(miner, events, bandwidth):
    current_bandwidth = bandwidth
    events.sort(key=lambda e: e.timestamp)
    while len(events) > 0 \
            and events[0].timestamp <= miner.clock \
            and current_bandwidth > 0:
        current_event = events.pop(0)
        if current_event.process(miner):
            current_bandwidth -= 1


class ReceiveNewBlockEvent(Event):
    def __init__(self, timestamp, block):
        super().__init__(timestamp)
        self.block = block
        self.type = EventType.RECV_NEW_BLOCK
        self.direction = 0 # 0 for download, 1 for upload

    def process(self, miner):
        if self.block.id not in miner.notified_blocks:
            miner.notify_neighbours(self.block)

        return miner.update_blockchain(self.block)


class SendNewBlockEvent(Event):
    def __init__(self, timestamp, block, dest):
        super().__init__(timestamp)
        self.block = block
        self.dest = dest
        self.type = EventType.SEND_NEW_BLOCK
        self.direction = 1 # 0 for download, 1 for upload

    def process(self, miner):
        miner.notified_blocks.append(self.block.id)
        new_event = ReceiveNewBlockEvent(miner.clock + miner.delay, self.block)
        update_event(new_event, self.dest.recv_events)
        return True


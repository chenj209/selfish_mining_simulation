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
    if new_event.timestamp not in events:
        events[new_event.timestamp] = []
    events[new_event.timestamp].append(new_event)

def process_event(miner, events_dict, bandwidth):
    current_bandwidth = bandwidth
    passed_timestamps = list(events_dict.keys())
    passed_timestamps.sort()
    i = 0
    while i < len(passed_timestamps) and current_bandwidth > 0:
        events = events_dict[passed_timestamps[i]]
        while len(events) > 0 \
                and events[0].timestamp <= miner.clock \
                and current_bandwidth > 0:
            current_event = events.pop(0)
            if current_event.process(miner):
                current_bandwidth -= 1
        if len(events) == 0:
            del events_dict[passed_timestamps[i]]
        i += 1


class ReceiveNewBlockEvent(Event):
    def __init__(self, timestamp, block):
        super().__init__(timestamp)
        self.block = block
        self.type = EventType.RECV_NEW_BLOCK
        self.direction = 0 # 0 for download, 1 for upload

    def process(self, miner):
        if miner.update_blockchain(self.block):
            miner.notify_neighbours(self.block)
            return True
        return False


class SendNewBlockEvent(Event):
    def __init__(self, timestamp, block, dest):
        super().__init__(timestamp)
        self.block = block
        self.dest = dest
        self.type = EventType.SEND_NEW_BLOCK
        self.direction = 1 # 0 for download, 1 for upload

    def process(self, miner):
        new_event = ReceiveNewBlockEvent(miner.clock + miner.delay, self.block)
        update_event(new_event, self.dest.recv_events)
        return True


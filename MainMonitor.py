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
from Miner import Miner
from NetworkTopology import NetworkGraphGen
import random
random.seed(2125)

class MainMonitor:
    def __init__(self, pow, miner_count, neighbour_count, delay, bandwidth, hash_power=1):
        # init <miner_count> miners
        self.pow = pow
        self.miners = [Miner(i, pow, delay, bandwidth, hash_power) for i in range(miner_count)]
        NetworkGraphGen.random_graph(self.miners, neighbour_count)
        self.clock = 0

    def run_simulation(self, time):
        blocks = {0: self.pow.prime_block}
        # dict{block_id: (block object, propagate count)}
        while self.clock < time:
            random.shuffle(self.miners)
            for miner in self.miners:
                new_blocks = miner.run()
                for new_block in new_blocks:
                    blocks[new_block.id] = new_block
            self.clock += 1
            if self.clock % 10 == 0:
                print(f"Clock: {self.clock}, Block Count: {pow.block_count}")
                # print(self.pow.prime_block.subtree_str(blocks))
                print(self.pow.prime_block.subtree_str(blocks))
                print("=====================================================")


if __name__ == '__main__':
    from POW import POW
    pow = POW(10, 100000)
    monitor = MainMonitor(pow, miner_count=1000, neighbour_count=128, delay=5, bandwidth=10, hash_power=1)
    # monitor = MainMonitor(pow, miner_count=1000, neighbour_count=128, delay=2, bandwidth=32, hash_power=1)
    monitor.run_simulation(2000)





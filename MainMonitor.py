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

class MainMonitor:
    def __init__(self, pow, miner_count, neighbour_count, delay, bandwidth, hash_power=1):
        # init <miner_count> miners
        self.pow = pow
        self.miners = [Miner(i, pow, delay, bandwidth) for i in range(miner_count)]
        NetworkGraphGen.random_graph(self.miners, neighbour_count)
        self.clock = 0

    def run_simulation(self, time):
        blocks = {0: self.pow.prime_block}
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
    pow = POW(20, 10000)
    monitor = MainMonitor(pow, miner_count=1000, neighbour_count=32, delay=20, bandwidth=100, hash_power=1000)
    monitor.run_simulation(100)





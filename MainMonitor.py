PLOT_GRAPHVIZ = True
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
from Miner import Miner, SelfishMiner, SelfishPropagator
from NetworkTopology import NetworkGraphGen
import random
# import networkx as nx
# import matplotlib.pyplot as plt
from graphviz import Digraph


random.seed(2125)

class MainMonitor:
    def __init__(self, pow, miner_count, neighbour_count, delay, bandwidth, hash_power=1, configuration="selfish1"):

        # init <miner_count> miners
        self.pow = pow
        if configuration == "selfish1":
            selfish_miner = [SelfishMiner(0, pow, delay, bandwidth, 430)]
            selfish_propagaters = [SelfishPropagator(selfish_miner[0], i, pow, delay, bandwidth) for i in range(1,100)]
            self.miners = [Miner(i, pow, delay, bandwidth, hash_power) for i in range(100, 100+miner_count)] \
                            + selfish_miner + selfish_propagaters
        else:
            self.miners = [Miner(i, pow, delay, bandwidth, hash_power) for i in range(miner_count)]
        NetworkGraphGen.random_graph(self.miners, neighbour_count)
        self.clock = 0

    def run_simulation(self, time):
        blocks = {0: self.pow.prime_block}
        G = Digraph(comment="Blockchain state")
        G.node(str(self.pow.prime_block.id), label=str(self.pow.prime_block))
        # dict{block_id: (block object, propagate count)}
        while self.clock < time:
            random.shuffle(self.miners)
            new_block_flag = False
            for miner in self.miners:
                new_blocks = miner.run()
                for new_block in new_blocks:
                    new_block_flag = True
                    blocks[new_block.id] = new_block
                    G.node(str(new_block.id), label=str(new_block))
                    G.edge(str(new_block.id), str(blocks[new_block.parent_id].id))
            self.clock += 1
            if self.clock % 10 == 0:
                print(f"Clock: {self.clock}, Block Count: {pow.block_count}")
            # if new_block_flag:
                print(self.pow.prime_block.subtree_str(blocks))
                if PLOT_GRAPHVIZ is True:
                    G.render('test-output/blockchain.gv', view=True)
                # print(self.pow.prime_block.subtree_str(blocks))
                # print("=====================================================")
                # nx.draw_planar(G, with_labels=True)
                # nx.draw_kamada_kawai(G, with_labels=True)
                # nx.draw_networkx(G,with_labels=True)
                # nx.draw(G, with_labels=True)


if __name__ == '__main__':
    from POW import POW
    pow = POW(10, 100000)
    monitor = MainMonitor(pow, miner_count=1000, neighbour_count=32, delay=1, bandwidth=10, hash_power=1)
    # monitor = MainMonitor(pow, miner_count=1000, neighbour_count=128, delay=2, bandwidth=32, hash_power=1)
    monitor.run_simulation(100)





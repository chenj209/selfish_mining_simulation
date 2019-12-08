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
        # dict{block_id: (block object, propagate count)}

        # HC: last block storage
        last_block_id = 0
        # HC #

        while self.clock < time:
            random.shuffle(self.miners)
            new_block_flag = False
            for miner in self.miners:
                new_blocks = miner.run()
                # HC: record new highest height
                if len(new_blocks) >= 1:
                    last_block_id = new_blocks[0].id
                # HC #

                for new_block in new_blocks:
                    new_block_flag = True
                    blocks[new_block.id] = new_block
            self.clock += 1
            if self.clock % 10 == 0 or new_block_flag:
                print(f"Clock: {self.clock}, Block Count: {pow.block_count}")
            if new_block_flag:
                G = Digraph(comment="Blockchain state", format='png')
                G.node(str(self.pow.prime_block.id), label=str(self.pow.prime_block))
                for id in blocks:
                    block = blocks[id]
                    if id != 0:
                        G.node(str(block.id), label=str(block), color=f"{'grey' if block.notified_miner_count == 0 else 'black'}")
                        G.edge(str(block.id), str(blocks[block.parent_id].id))
                print(self.pow.prime_block.subtree_str(blocks))
                if PLOT_GRAPHVIZ is True:
                    G.render(f'test-output/blockchain-clock-{self.clock}.gv', view=True)
                # print(self.pow.prime_block.subtree_str(blocks))
                # print("=====================================================")
                # nx.draw_planar(G, with_labels=True)
                # nx.draw_kamada_kawai(G, with_labels=True)
                # nx.draw_networkx(G,with_labels=True)
                # nx.draw(G, with_labels=True)

        regular_rewards, uncle_rewards = self.reward(blocks, last_block_id)
    
    # assume a block earns the miner 32 unit 
    def reward(self, blocks, last_block_id):
        longest_chain = self.find_longest_chain(blocks, last_block_id)
        uncles, nephews = self.find_uncles_nephews(blocks, longest_chain)
        # regular reward dict {miner_id: reward}
        regular_rewards = {}
        # uncle reward dict {miner_id: reward}
        uncle_rewards = {}

        # assign regular block reward
        for regular_block in longest_chain:
            # miner_id does not exist yet
            if regular_block.miner_id not in regular_rewards:
                regular_rewards[regular_block.miner_id] = 32
            # miner_id alreay exists
            else:
                regular_rewards[regular_block.miner_id] += 32
        
        # assign nephew block reward
        for nephew_block in nephews:
            regular_rewards[nephew_block.miner_id] += 1

        # assign uncle block reward
        uncle_ids = uncles.keys()
        for uncle_id in uncle_ids:
            temp_miner_id = blocks[uncle_id].miner_id
            # update key
            if temp_miner_id not in uncle_rewards:
                uncle_rewards[temp_miner_id] = 0
            # compute reward amount
            if uncles[uncle_id] <= 6:
                temp_reward = (8 - uncles[uncle_id])*4
                uncle_rewards[temp_miner_id] += temp_reward
            # trivia but save for future modification
            else:
                temp_reward = 0
                uncle_rewards[temp_miner_id] += temp_reward
    
        return regular_rewards, uncle_rewards

    def find_longest_chain(self, blocks, last_block_id):
        # longest chain list
        longest_chain = []
        # start from the last block
        temp_child_block = blocks[last_block_id]
        while temp_child_block.id != 0:
            longest_chain.append(temp_child_block)
            temp_parent_block = blocks[temp_child_block.parent_id]
            temp_child_block = temp_parent_block
        longest_chain.append(temp_child_block)
        return longest_chain
    
    def find_uncles_nephews(self, blocks, longest_chain):
        # uncle dict {uncle_id:distance}
        uncles = {}
        # nephew list
        nephews = []
        # start from the first element of longest chain (last block)
        for regular_block in longest_chain:
            if len(regular_block.uncles) >= 1:
                # update nephew list
                nephews.append(regular_block)
                # update uncle dict
                for uncle_id in regular_block.uncles:
                    distance = regular_block.height - blocks[uncle_id].height
                    uncles[uncle_id] = distance
        
        return uncles, nephews
    
if __name__ == '__main__':
    from POW import POW
    pow = POW(10, 100000)
    monitor = MainMonitor(pow, miner_count=1000, neighbour_count=32, delay=1, bandwidth=10, hash_power=1)
    # monitor = MainMonitor(pow, miner_count=1000, neighbour_count=128, delay=2, bandwidth=32, hash_power=1)
    random.seed(2125)
    monitor.run_simulation(200)





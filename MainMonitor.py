import math
import sys
sys.setrecursionlimit(10000)
from Block import Block

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
from POW import POW


class MainMonitor:
    def __init__(self, pow, miner_count, neighbour_count, delay, upload_bandwidth, download_bandwidth,
                 hash_power=1, selfish_miner_hash_power_in_percent=0.3, propagator_count=100,
                 propagator_delay=0, propagator_upload_bandwidth=100, propagator_download_bandwidth=100, racing_test=False, race_count=0):

        self.hash_power = hash_power
        self.selfish_miner_hash_power_in_percent = selfish_miner_hash_power_in_percent
        self.racing_test = racing_test
        self.race_count = race_count
        if not racing_test:
            # init <miner_count> miners
            self.pow = pow
            self.miner_count = miner_count
            self.propagater_count = propagator_count
            self.selfish_miner = None
            # if configuration == "selfish1":
            selfish_miner_hr = math.ceil(hash_power*miner_count/(1-selfish_miner_hash_power_in_percent)-miner_count*hash_power)
            self.selfish_miner = SelfishMiner(0, pow, delay, upload_bandwidth, download_bandwidth, selfish_miner_hr)
            selfish_propagaters = [SelfishPropagator(self.selfish_miner, i, pow, propagator_delay, propagator_upload_bandwidth, propagator_download_bandwidth) for i in range(1+self.miner_count,1+self.miner_count+self.propagater_count)]
            self.miners = [Miner(i, pow, delay, upload_bandwidth, download_bandwidth, hash_power) for i in range(1, miner_count+1)] \
                            + [self.selfish_miner] + selfish_propagaters
            # else:
            #     self.miners = [Miner(i, pow, delay, bandwidth, hash_power) for i in range(miner_count)]
            NetworkGraphGen.random_graph(self.miners, neighbour_count)
            self.clock = 0
            self.propagation_rates = []

        else:
            # init <miner_count> miners
            self.pow = POW(1,1)
            self.miner_count = miner_count
            self.propagater_count = propagator_count
            self.selfish_miner = None
            # if configuration == "selfish1":
            self.selfish_miner = SelfishMiner(0, self.pow, delay, upload_bandwidth, download_bandwidth, 1)
            self.selfish_miner.racing_test = True
            racer_miner = Miner(1, self.pow, delay, upload_bandwidth, download_bandwidth, 1)
            selfish_propagaters = [SelfishPropagator(self.selfish_miner, i, self.pow, propagator_delay, propagator_upload_bandwidth, propagator_download_bandwidth) for i in range(1+self.miner_count,1+self.miner_count+self.propagater_count)]
            self.miners = [Miner(i, self.pow, delay, upload_bandwidth, download_bandwidth, 0) for i in range(2, miner_count+1)] \
                          + [self.selfish_miner] + [racer_miner] + selfish_propagaters
            # else:
            #     self.miners = [Miner(i, pow, delay, bandwidth, hash_power) for i in range(miner_count)]
            NetworkGraphGen.random_graph(self.miners, neighbour_count)
            self.clock = 0
            self.propagation_rates = []

    def run_simulation(self, time):
        blocks = {0: self.pow.prime_block}
        # dict{block_id: (block object, propagate count)}
        longest_chain_height = 1

        # HC: last block storage
        last_block_id = 0
        # HC #

        # while (self.racing_test or self.clock < time) and (not self.racing_test or len(self.propagation_rates) < self.race_count):
        while (self.racing_test or self.pow.block_count < time) and (
                    not self.racing_test or len(self.propagation_rates) < self.race_count):
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
                    if new_block.height > longest_chain_height:
                        longest_chain_height = new_block.height

            if len(self.selfish_miner.racing_blocks) > 0:
                racing_blocks = self.selfish_miner.racing_blocks[:]
                for block in racing_blocks:
                    if block.notified_miner_count == self.miner_count + self.propagater_count + 1:
                        pr = block.win_race_count / self.miner_count
                        self.propagation_rates.append(pr)
                        print(f"Race finish, propagation rate: {pr}")
                        self.selfish_miner.racing_blocks.remove(block)

            self.clock += 1
            if self.clock % 100 == 0 or new_block_flag:
                print(f"Clock: {self.clock}, Block Count: {self.pow.block_count}")
                if self.racing_test:
                    print(f"Race count: {len(self.propagation_rates)}")
            # if new_block_flag and not self.racing_test:
            #     G = Digraph(comment="Blockchain state", format='png')
            #     G.node(str(self.pow.prime_block.id), label=str(self.pow.prime_block))
            #     for id in blocks:
            #         block = blocks[id]
            #         if id != 0:
            #             G.node(str(block.id), label=str(block), color=f"{'grey' if block.notified_miner_count == 0 else 'black'}")
            #             G.edge(str(block.id), str(blocks[block.parent_id].id))
            #     print(self.pow.prime_block.subtree_str(blocks))
                '''
                if PLOT_GRAPHVIZ is True:
                    G.render(f'test-output/blockchain-clock-{self.clock}.gv', view=True)
                '''
                # print(self.pow.prime_block.subtree_str(blocks))
                # print("=====================================================")
                # nx.draw_planar(G, with_labels=True)
                # nx.draw_kamada_kawai(G, with_labels=True)
                # nx.draw_networkx(G,with_labels=True)
                # nx.draw(G, with_labels=True)
        if len(self.propagation_rates) > 0:
            print(f"Avg propagation rate: {sum(self.propagation_rates) / len(self.propagation_rates)}")
            print(f"Propagation race results: {self.propagation_rates}")
        else:
            print("No propagation race")
        regular_rewards, uncle_rewards = self.reward(blocks, last_block_id)
        total_rewards = sum(regular_rewards.values())+sum(uncle_rewards.values())
        selfish_rewards = regular_rewards.get(0, 0)+uncle_rewards.get(0, 0)
        print("Total reward ratio:", selfish_rewards, " / ", total_rewards)
        print("Uncle reward ratio:", uncle_rewards.get(0, 0), " / ", sum(uncle_rewards.values()))
        print("Regular reward ratio:", regular_rewards.get(0, 0), " / ", sum(regular_rewards.values()))
        print("Selfish rewards:", regular_rewards.get(0, 0)+uncle_rewards.get(0, 0))
        print("Selfish rewards ratio:", (regular_rewards.get(0, 0) + uncle_rewards.get(0, 0))/total_rewards)
        output = f"Selfish hr in percent: {self.selfish_miner_hash_power_in_percent}\n" \
            + f"Selfish rewards ratio: {(regular_rewards.get(0, 0) + uncle_rewards.get(0, 0))/total_rewards}\n" \
            + f"Total reward ratio: {selfish_rewards} / {total_rewards}\n" \
            + f"Uncle reward ratio: {uncle_rewards.get(0, 0)} / {sum(uncle_rewards.values())} \n" \
            + f"Regular reward ratio: {regular_rewards.get(0, 0)} / {sum(regular_rewards.values())}\n"



        print("regular reward dictionary:")
        print(regular_rewards)
        print("uncle reward dictionary:")
        print(uncle_rewards)
        #selfish_miner_rewards = regular_rewards[0]+uncle_rewards[0]
        #print(selfish_miner_rewards)
        print("Simulation Done!")
        return output


    # assume a block earns the miner 32 unit
    def reward(self, blocks, last_block_id):
        longest_chain = self.find_longest_chain(blocks, last_block_id)
        new_blocks = self.assign_uncles(blocks, longest_chain)
        # new_blocks = self.assign_uncles_all_selfish(blocks, longest_chain)
        uncles, nephews = self.find_uncles_nephews(new_blocks, longest_chain)
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
            # print("len(nephew_block.uncles): ", len(nephew_block.uncles))
            regular_rewards[nephew_block.miner_id] += len(nephew_block.uncles)

        '''
        # assign nephew block reward
        for nephew_block in nephews:
            regular_rewards[nephew_block.miner_id] += 1
            
        '''

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

        '''
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
        '''

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


    def assign_uncles(self, blocks, longest_chain):
        print("start assign_uncles")
        rev_longest_chain = longest_chain[-3::-1] # skip first two blocks
        uncle_candidates = self.find_uncle_candidates(blocks, longest_chain)
        for regular_block in rev_longest_chain:
            #
            # if this regular block is mined by a selfish miner (Rational)
            if regular_block.miner_id == 0:
                # self uncle check count
                if regular_block.height < 6:
                    generation_count = regular_block.height - 2
                else:
                    generation_count = 6
                # find uncles mined by itself from current to previous height
                for i in range(regular_block.height, regular_block.height-generation_count, -1):
                    if i in uncle_candidates:
                        for uncle_id in uncle_candidates[i]:
                            print("0uncle_id:", uncle_id)
                            #print("regular_block uncle test:", len(regular_block.uncles),"answer: ", regular_block.need_more_uncles())
                            print("regular_block uncle test:", len(regular_block.uncles), "answer: ", regular_block.need_more_uncles())
                            print("blocks[uncle_id].miner_id == regular_block.miner_id:", "answer: ", blocks[uncle_id].miner_id == regular_block.miner_id)
                            print("blocks[uncle_id].publish_timestamp <= regular_block.timestamp", "answer: ", blocks[uncle_id].publish_timestamp <= regular_block.timestamp)
                            if regular_block.need_more_uncles() and blocks[uncle_id].miner_id == regular_block.miner_id \
                                    and blocks[uncle_id].publish_timestamp <= regular_block.timestamp:
                                blocks[regular_block.id].uncles.append(uncle_id)
                                # remove uncle_id
                                print("0before remove:", uncle_candidates[i])
                                uncle_candidates[i].remove(uncle_id)
                                print("0after remove:", uncle_candidates[i])
                        '''
                        # remove this entry if its empty
                        if len(uncle_candidates[i]) == 0:
                            del uncle_candidates[i]
                        '''


                # find uncles mined by anyone
                #while regular_block.need_more_uncles and len(uncle_candidates) > 0:
                    #temp_list = uncle_candidates.keys().copy()
                for j in uncle_candidates.keys():

                    if j < regular_block.height:
                        for uncle_id in uncle_candidates[j]:
                            print("1uncle_id:", uncle_id)
                            # print("regular_block uncle test:", len(regular_block.uncles), "answer: ", regular_block.need_more_uncles())
                            print("regular_block uncle test:", len(regular_block.uncles), "answer: ", regular_block.need_more_uncles())
                            print("blocks[uncle_id].timestamp < regular_block.timestamp:", "answer: ", blocks[uncle_id].timestamp < regular_block.timestamp)
                            if regular_block.need_more_uncles() and blocks[uncle_id].timestamp < regular_block.timestamp:
                                blocks[regular_block.id].uncles.append(uncle_id)
                                # remove uncle_id
                                print("1before remove:", uncle_candidates[j])
                                uncle_candidates[j].remove(uncle_id)
                                print("1after remove:", uncle_candidates[j])
                        '''
                        # remove this entry if its empty
                        if len(uncle_candidates[j]) == 0:
                            del uncle_candidates[j]
                        '''

            # regular block mined by honest miner
            else:
                #while regular_block.need_more_uncles and len(uncle_candidates) > 0:
                    # temp_list = uncle_candidates.keys().copy()
                for k in uncle_candidates.keys():

                    if k < regular_block.height:
                        for uncle_id in uncle_candidates[k]:
                            print("2uncle_id:", uncle_id)
                            print("regular_block uncle test:", len(regular_block.uncles), "answer: ", regular_block.need_more_uncles())
                            print("blocks[uncle_id].timestamp < regular_block.timestamp:", "answer: ", blocks[uncle_id].timestamp < regular_block.timestamp)
                            print("(blocks[uncle_id].miner_id != 0", "answer: ", (blocks[uncle_id].miner_id != 0))
                            # print("regular_block uncle test:", len(regular_block.uncles), "answer: ", regular_block.need_more_uncles())
                            if regular_block.need_more_uncles() and blocks[uncle_id].timestamp < regular_block.timestamp and (blocks[uncle_id].miner_id != 0):
                                blocks[regular_block.id].uncles.append(uncle_id)
                                # remove uncle_id
                                print("2before remove:", uncle_candidates[k])
                                uncle_candidates[k].remove(uncle_id)
                                print("2after remove:", uncle_candidates[k])
                            print("regular_block uncle test:", len(regular_block.uncles), "answer: ", regular_block.need_more_uncles())
                            print("blocks[uncle_id].publish_timestamp < regular_block.timestamp:", "answer: ", blocks[uncle_id].publish_timestamp < regular_block.timestamp)
                            print("(blocks[uncle_id].miner_id == 0", "answer: ", (blocks[uncle_id].miner_id == 0))
                            if regular_block.need_more_uncles() and blocks[uncle_id].publish_timestamp < regular_block.timestamp and (blocks[uncle_id].miner_id == 0):
                                blocks[regular_block.id].uncles.append(uncle_id)
                                # remove uncle_id
                                print(regular_block.id)
                                print("3before remove:", uncle_candidates[k])
                                uncle_candidates[k].remove(uncle_id)
                                print("3after remove:", uncle_candidates[k])
                        '''
                        # remove this entry if its empty
                        if len(uncle_candidates[k]) == 0:
                            del uncle_candidates[k]
                        '''
        print("Uncles have been assigned!")
        return blocks

    def assign_uncles_all_selfish(self, blocks, longest_chain):
        print("start assign_uncles")
        rev_longest_chain = longest_chain[-3::-1] # skip first two blocks
        uncle_candidates = self.find_uncle_candidates(blocks, longest_chain)
        for regular_block in rev_longest_chain:
            #
            # if this regular block is mined by a selfish miner (Rational)
            if regular_block.miner_id == 0:
                # self uncle check count
                if regular_block.height < 6:
                    generation_count = regular_block.height - 2
                else:
                    generation_count = 6
                # find uncles mined by itself from current to previous height
                for i in range(regular_block.height, regular_block.height-generation_count, -1):
                    if i in uncle_candidates:
                        for uncle_id in uncle_candidates[i]:
                            if regular_block.need_more_uncles and blocks[uncle_id].miner_id == regular_block.miner_id:
                                blocks[regular_block.id].uncles.append(uncle_id)
                                # remove uncle_id
                                uncle_candidates[i].remove(uncle_id)
                        '''
                        # remove this entry if its empty
                        if len(uncle_candidates[i]) == 0:
                            del uncle_candidates[i]
                        '''


                # find uncles mined by anyone
                #while regular_block.need_more_uncles and len(uncle_candidates) > 0:
                    #temp_list = uncle_candidates.keys().copy()
                for j in uncle_candidates.keys():
                    if j < regular_block.height:
                        for uncle_id in uncle_candidates[j]:
                            if regular_block.need_more_uncles and blocks[uncle_id].timestamp < regular_block.timestamp:
                                blocks[regular_block.id].uncles.append(uncle_id)
                                # remove uncle_id
                                uncle_candidates[j].remove(uncle_id)
                        '''
                        # remove this entry if its empty
                        if len(uncle_candidates[j]) == 0:
                            del uncle_candidates[j]
                        '''


            # regular block mined by honest miner
            else:
                #while regular_block.need_more_uncles and len(uncle_candidates) > 0:
                    # temp_list = uncle_candidates.keys().copy()
                for k in uncle_candidates.keys():
                    if k < regular_block.height:
                        for uncle_id in uncle_candidates[k]:
                            if regular_block.need_more_uncles and blocks[uncle_id].timestamp < regular_block.timestamp\
                                    and blocks[uncle_id].miner_id == regular_block.miner_id:
                                blocks[regular_block.id].uncles.append(uncle_id)
                                # remove uncle_id
                                uncle_candidates[k].remove(uncle_id)
                        '''
                        # remove this entry if its empty
                        if len(uncle_candidates[k]) == 0:
                            del uncle_candidates[k]
                        '''
        print("Uncles have been assigned!")
        return blocks









    def find_uncle_candidates(self, blocks, longest_chain):
        # rev_longest_chain = longest_chain[::-1]
        uncle_candidates = {}  # {height:[uncle_id_1, uncle_id_2 ...]}
        temp_last_regular_block = Block(-1, -1, -1, -1, -1)
        for regular_block in longest_chain:
            if len(regular_block.children) >= 1:
                for child_id in regular_block.children:
                    # not in the longest chain
                    if child_id != temp_last_regular_block.id:
                        if blocks[child_id].height not in uncle_candidates:
                            uncle_candidates[blocks[child_id].height] = [child_id]
                        else:
                            uncle_candidates[blocks[child_id].height].append(child_id)
            temp_last_regular_block = regular_block
        print("uncle_candidates", uncle_candidates)

        return uncle_candidates

def main(config_file='selfish_config.json'):
    config = json.load(open(config_file))
    pow = POW(config['pow_difficulty']*100000000000, 100000000000)
    random.seed(config['random_seed'])
    hrs = config.get('hrs', [])
    if len(hrs) > 0:
        for hr in hrs:
            print(f"Running {hr}")
            pow = POW(config['pow_difficulty'] * 100000000000, 100000000000)
            random.seed(config['random_seed'])
            monitor = MainMonitor(pow, miner_count=config['miner_count'], neighbour_count=config['neighbour_count'],
                                  delay=config['network_delay'], upload_bandwidth=config['network_upload_bandwidth'],
                                  download_bandwidth=config['network_download_bandwidth'],
                                  hash_power=config['hash_power_per_miner'],
                                  selfish_miner_hash_power_in_percent=hr,
                                  propagator_count=config['selfish_propagator_count'],
                                  propagator_delay=config['propagator_delay'],
                                  propagator_upload_bandwidth=config['propagator_upload_bandwidth'],
                                  propagator_download_bandwidth=config['propagator_download_bandwidth'],
                                  racing_test=bool(config['racing_test']),
                                  race_count=config['race_count'])
            output = "Selfish\n" + monitor.run_simulation(config['simulation_blocks'])
            with open(f"selfish_hash_power_{hr}", "w") as f:
                f.write(output)
            pow = POW(config['pow_difficulty'] * 100000000000, 100000000000)
            random.seed(config['random_seed'])
            monitor = MainMonitor(pow, miner_count=config['miner_count'], neighbour_count=config['neighbour_count'],
                                  delay=config['network_delay'], upload_bandwidth=config['network_upload_bandwidth'],
                                  download_bandwidth=config['network_download_bandwidth'],
                                  hash_power=config['hash_power_per_miner'],
                                  selfish_miner_hash_power_in_percent=hr,
                                  propagator_count=config['selfish_propagator_count'],
                                  propagator_delay=config['propagator_delay'],
                                  propagator_upload_bandwidth=config['propagator_upload_bandwidth'],
                                  propagator_download_bandwidth=config['propagator_download_bandwidth'],
                                  racing_test=bool(config['racing_test']),
                                  race_count=config['race_count'])
            monitor.selfish_miner.honest = True
            output = "Honest\n" + monitor.run_simulation(config['simulation_blocks'])
            with open(f"honest_hash_power_{hr}", "w") as f:
                f.write(output)
    else:



        monitor = MainMonitor(pow, miner_count=config['miner_count'], neighbour_count=config['neighbour_count'],
                              delay=config['network_delay'], upload_bandwidth=config['network_upload_bandwidth'],
                              download_bandwidth=config['network_download_bandwidth'],
                              hash_power=config['hash_power_per_miner'], selfish_miner_hash_power_in_percent=config['selfish_miner_hash_power_in_percent'],
                              propagator_count=config['selfish_propagator_count'], propagator_delay=config['propagator_delay'],
                              propagator_upload_bandwidth=config['propagator_upload_bandwidth'], propagator_download_bandwidth=config['propagator_download_bandwidth'], racing_test=bool(config['racing_test']),
                              race_count=config['race_count'])
        if config['honest_test']:
            monitor.selfish_miner.honest = True
        monitor.run_simulation(config['simulation_blocks'])


if __name__ == '__main__':
    import json
    from fire import Fire
    Fire(main)





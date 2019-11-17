import random
import time

# one central node, receive request from all other nodes
# other nodes runs local pow
class BlockChain:
    def __init__(self, chain_id, propagation_power):
        """
        Args:
            propagation_power (int): a number representing the power of be propagated,
                                     if there are multiple chains of same length exists, the break tie rule would be
                                     random selection using propagation_power / sum(all_propagation_power)
            other chains of the same length
        """
        self.chain_id = chain_id
        self.chain = []
        self.propagation_power = propagation_power

    def __str__(self):
        return str(self.chain)

    def append_chain(self, miner_id):
        self.chain.append(miner_id)

    def successor(self, other_chain):
        """
        returns the longer chain is the longer one of this chain and other chain extends the shorter one
        Args:
            other_chain (BlockChain): other blochchain object

        Returns:
            None if not successor relationship, else the longer chain
        """
        longer = self
        shorter = other_chain
        if len(other_chain.chain) > len(self.chain):
            longer = other_chain
            shorter = self
        if longer.chain[:len(shorter.chain)] == shorter.chain:
            return longer

class BlockChainTree:
    def __init__(self):
        self.longest = []
        self.tree = {}
        self.count = 0

    def __str__(self):
        return f"""
        ==============================================================================================================
        Longest: {[str(c) for c in self.longest]}
        
        ==============================================================================================================
        """

    def update(self, chain):
        if chain.chain_id not in self.tree:
            new_chain = chain
        else:
            successor = self.tree[chain.chain_id].successor(chain)
            if successor:
                new_chain = successor
            else:
                chain.chain_id = self.count + 1
                new_chain = chain
        self.tree[new_chain.chain_id] = new_chain
        if len(self.longest) == 0 or len(new_chain.chain) == len(self.longest[0].chain):
            self.longest.append(new_chain)
        elif len(new_chain.chain) > len(self.longest[0].chain):
            self.longest = [new_chain]

    def get_longest_chain(self):
        if len(self.longest) == 0:
            return BlockChain(0, 1)
        sum_propagation_power = sum([c.propagation_power for c in self.longest])
        return random.choices(self.longest, [c.propagation_power / sum_propagation_power for c in self.longest])[0]


class POW:
    def __init__(self, difficulty, difficulty_bound):
        """
        Create a POW with <difficulty> parameter. A miner will run a random number generator to produce a number
        between 0 and 100000. If the number generated is smaller than difficulty, the POW is valid
        Args:
            difficulty (int): difficulty of POW
        """
        self.difficulty = difficulty
        self.bound = difficulty_bound

    def try_POW(self):
        nounce = random.randint(0, self.bound)
        if nounce < self.difficulty:
            return nounce

class MonitorNode:
    def __init__(self, comm, pow, bandwidth = 0, network_delay = 0):
        """
        Args:
            comm: Communication world object
            bandwidth (int): number of request that can be broadcast in the network per minute
            network_delay: in sec the delay to broadcast a message
        """
        print("Monitor Running...")
        self.comm = comm
        self.bandwidth = bandwidth
        self.network_delay = network_delay
        self.pow = pow
        self.blockchains = BlockChainTree()

    def run(self, simulation_time):
        counter = 0
        start = int(time.time())
        responses = {}
        # assumes monitor node is rank 0
        for i in range(1, self.comm.size):
            responses[i] = self.comm.irecv(source=i)
        past_time = None

        # send blockchain tree initial state
        self.comm.bcast(self.blockchains, root=0)
        while time.time() - start < simulation_time:
            update_flag = False
            for i in range(1, self.comm.size):
                # check if target miner has a solution
                res = responses[i].test()
                if res[0]:
                    update_flag = True
                    self.blockchains.update(res[1])
                    responses[i] = self.comm.irecv(source=i)

            if update_flag:
                # broadcast the newest blockchain state
                blockchains = self.blockchains
                for i in range(1, self.comm.size):
                    self.comm.isend(blockchains, dest=i, tag=0)
                print(blockchains)

            current_time = int(time.time()) - start
            if current_time % 5 == 0 and past_time != current_time:
                print(f"Time: {current_time} sec")
                past_time = current_time


class MinerNode:
    def __init__(self, comm, id, pow, compute_delay):
        print(f"Miner {id} running...")
        self.comm = comm
        self.id = id
        self.pow = pow
        self.compute_delay = compute_delay

    def run(self, simulation_time):
        start = time.time()
        blockchains = None
        # collect initial blockchain tree
        blockchains = self.comm.bcast(blockchains, root=0)

        # initial blockchain update request from monitor node
        bc_update_req = self.comm.irecv(source=0, tag=0)

        while time.time() - start < simulation_time:
            # check if there is update to the blockchain tree
            res = bc_update_req.test()
            if res[0]:
                blockchains = res[1]
                bc_update_req = self.comm.irecv(source=0, tag=0)

            # start mining
            nounce = self.pow.try_POW()
            time.sleep(self.compute_delay)
            if nounce:
                print(f"Miner {rank} finds a block!")
                chain = blockchains.get_longest_chain()
                chain.append_chain(self.id)
                self.comm.isend(chain, dest=0)

if __name__ == '__main__':
    from mpi4py import MPI
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    pow = POW(10, 100)
    if rank == 0:
        monitor = MonitorNode(comm, pow)
        monitor.run(60)
    else:
        miner = MinerNode(comm, rank, pow)
        miner.run(60)


















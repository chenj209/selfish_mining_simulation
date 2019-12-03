import random
from Block import Block


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
        # self.count = 0
        self.block_count = 1 # keep track of global block count
        self.prime_block = Block(0, -1, 0, -1, 1)
        self.prime_block.notified_miner_count = 1000

    def try_POW(self):
        nounce = random.randint(0, self.bound)
        # self.count += 1
        # if self.count % 100 == 0:
        #     print(f"POW is tried {self.count} times")

        if nounce < self.difficulty:
            # self.count = 0
            self.block_count += 1
            return nounce
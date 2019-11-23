import random


class NetworkGraphGen:
    @staticmethod
    def random_graph(miners, neighbour_count):
        for i in range(len(miners)):
            miners[i].neighbours = random.sample(miners[:i] + miners[i+1:], neighbour_count)

import random
def crossover(a, b):
    point = random.randint(1, len(a)-1)
    return a[:point] + b[point:]

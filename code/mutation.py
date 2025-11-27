
import random
def mutate(schedule, rate=0.1):
    for s in schedule:
        if random.random() < rate:
            s['timeslot'] = random.randint(1,50)


import random

def mutate(schedule, rate=0.1):
    """
    Mutation: thay đổi ngẫu nhiên timeslot hoặc room của một số lớp
    """
    from genetic_algorithm import generate_preferred_timeslot, generate_random_room
    
    for i, cls in enumerate(schedule):
        if random.random() < rate:
            # 70% chance thay đổi timeslot, 30% chance thay đổi room
            if random.random() < 0.7:
                schedule[i]['timeslot'] = generate_preferred_timeslot()
            else:
                schedule[i]['room'] = generate_random_room()

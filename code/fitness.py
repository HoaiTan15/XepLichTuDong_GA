
def fitness_score(schedule):
    conflicts=0
    for i in range(len(schedule)):
        for j in range(i+1,len(schedule)):
            a = schedule[i]
            b = schedule[j]

            # Room conflict
            if a['room']==b['room'] and a['timeslot']==b['timeslot']:
                conflicts+=1

            # Teacher conflict
            if a['teacher']==b['teacher'] and a['timeslot']==b['timeslot']:
                conflicts+=1

    return 1/(1+conflicts)

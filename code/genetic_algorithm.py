
import random
import pandas as pd
from fitness import fitness_score
from crossover import crossover
from mutation import mutate

class GeneticAlgorithm:
    def __init__(self, df, population_size=60, generations=150):
        self.df = df
        self.population_size = population_size
        self.generations = generations

    def create_individual(self):
        schedule=[]
        for _, row in self.df.iterrows():
            schedule.append({
                "course_id": row['course_id'],
                "course_name": row['course_name'],
                "subject_code": row['subject_code'], 
                "section": row['section'],
                "teacher": row['teacher'],
                "room": row['room'],
                "timeslot": random.randint(1,50)
            })
        return schedule

    def create_population(self):
        return [self.create_individual() for _ in range(self.population_size)]

    def run(self):
        population = self.create_population()
        best=None

        for gen in range(self.generations):
            scored = [{"schedule":ind, "fitness":fitness_score(ind)} for ind in population]
            scored.sort(key=lambda x: x['fitness'], reverse=True)

            if best is None or scored[0]['fitness'] > best['fitness']:
                best = scored[0]

            # Selection
            survivors = scored[:20]
            new_pop = [s['schedule'] for s in survivors]

            # New generation
            while len(new_pop) < self.population_size:
                p1, p2 = random.sample(survivors, 2)
                child = crossover(p1['schedule'], p2['schedule'])
                mutate(child)
                new_pop.append(child)

            population = new_pop

        return best

    def export_excel(self, schedule):
        df = pd.DataFrame(schedule)
        filename = f"schedule_50classes_{pd.Timestamp.now().strftime('%H%M%S')}.xlsx"
        df.to_excel(filename, index=False)
        print(f"✅ Đã lưu: {filename}")

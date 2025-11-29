
import random
import pandas as pd
from fitness import fitness_score
from crossover import crossover
from mutation import mutate

def get_timeslot_detail(timeslot):
    """
    Chuyển đổi timeslot number thành mô tả chi tiết
    Mỗi ngày có 5 buổi: Sáng(1-3), Sáng(4-6), Chiều(7-9), Chiều(10-12), Tối(13-15)
    Tổng cộng: 7 ngày x 5 buổi = 35 timeslot
    """
    # Mapping timeslot theo thứ và ca (7 ngày từ Thứ 2 đến Chủ nhật)
    days = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]
    
    # Chia timeslot theo ngày (mỗi ngày có 5 buổi)
    day_index = (timeslot - 1) // 5
    session_in_day = (timeslot - 1) % 5 + 1
    
    day_name = days[day_index % 7]  # 7 ngày trong tuần
    
    # Map session sang tên buổi
    sessions = {
        1: "Sáng - Tiết 1-3",
        2: "Sáng - Tiết 4-6", 
        3: "Chiều - Tiết 7-9",
        4: "Chiều - Tiết 10-12",
        5: "Tối - Tiết 13-15"
    }
    
    return f"{day_name} - {sessions[session_in_day]}"

def generate_preferred_timeslot():
    """
    Tạo timeslot với ưu tiên:
    - 68% Thứ 2-6 sáng/chiều (timeslot 1-4 của mỗi ngày)
    - 12% Thứ 7 sáng/chiều (timeslot 26-29)
    - 15% Buổi tối Thứ 2-7 (timeslot 5, 10, 15, 20, 25, 30)
    - 5% Chủ nhật (timeslot 31-35)
    Tổng: 35 timeslot (7 ngày x 5 buổi)
    """
    rand = random.random()
    
    if rand < 0.68:  # 68% - Thứ 2-6 sáng/chiều
        day = random.randint(0, 4)  # Thứ 2-6 (ngày 0-4)
        session = random.randint(1, 4)  # Buổi 1-4 (sáng + chiều)
        return day * 5 + session
        
    elif rand < 0.8:  # 12% - Thứ 7 sáng/chiều  
        day = 5  # Thứ 7 (ngày 5)
        session = random.randint(1, 4)  # Buổi 1-4 (sáng + chiều)
        return day * 5 + session
        
    elif rand < 0.95:  # 15% - Buổi tối (Thứ 2-7)
        day = random.randint(0, 5)  # Thứ 2-7 (ngày 0-5)
        session = 5  # Buổi tối
        return day * 5 + session
        
    else:  # 5% - Chủ nhật (toàn bộ)
        day = 6  # Chủ nhật (ngày 6)
        session = random.randint(1, 5)  # Tất cả 5 buổi
        return day * 5 + session

def load_available_rooms():
    """
    Tải danh sách phòng học available
    """
    try:
        with open('available_rooms.txt', 'r') as f:
            rooms = [line.strip() for line in f.readlines()]
        return rooms
    except FileNotFoundError:
        # Nếu chưa có file, tạo default rooms
        default_rooms = []
        for floor in [1, 2, 3, 4]:
            for room_num in range(1, 11):
                default_rooms.append(f"A{floor}0{room_num}")
                default_rooms.append(f"B{floor}0{room_num}")
        return default_rooms

def generate_random_room():
    """
    Chọn ngẫu nhiên 1 phòng học từ danh sách available
    """
    available_rooms = load_available_rooms()
    return random.choice(available_rooms)

class GeneticAlgorithm:
    def __init__(self, df, population_size=50, generations=100):
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
                "room": generate_random_room(),  # GA tự động chọn phòng
                "timeslot": generate_preferred_timeslot()  # Sử dụng timeslot ưu tiên
            })
        return schedule

    def create_population(self):
        return [self.create_individual() for _ in range(self.population_size)]

    def run(self):
        population = self.create_population()
        best = None
        stagnant_count = 0
        
        print(f"🧬 Bắt đầu chạy GA với {self.population_size} cá thể, {self.generations} thế hệ...")

        for gen in range(self.generations):
            # Evaluate fitness
            scored = [{"schedule": ind, "fitness": fitness_score(ind)} for ind in population]
            scored.sort(key=lambda x: x['fitness'], reverse=True)

            # Track best solution
            if best is None or scored[0]['fitness'] > best['fitness']:
                best = scored[0].copy()
                stagnant_count = 0
                print(f"Gen {gen:3d}: Cải thiện! Fitness = {best['fitness']:.6f}")
            else:
                stagnant_count += 1

            # Early stopping nếu không cải thiện trong 20 thế hệ
            if stagnant_count > 20:
                print(f"⏹️ Dừng sớm ở thế hệ {gen} (không cải thiện)")
                break

            # Elitism: Giữ lại top 10% tốt nhất
            elite_size = max(2, self.population_size // 10)
            new_pop = [s['schedule'] for s in scored[:elite_size]]

            # Selection với tournament selection
            while len(new_pop) < self.population_size:
                # Tournament selection: chọn tốt nhất trong 3 cá thể ngẫu nhiên
                tournament1 = random.sample(scored[:self.population_size//2], min(3, len(scored)))
                tournament2 = random.sample(scored[:self.population_size//2], min(3, len(scored)))
                
                p1 = max(tournament1, key=lambda x: x['fitness'])
                p2 = max(tournament2, key=lambda x: x['fitness'])
                
                child = crossover(p1['schedule'], p2['schedule'])
                
                # Adaptive mutation: tăng mutation rate nếu stagnant
                mutation_rate = 0.1 + (stagnant_count * 0.02)
                mutate(child, rate=min(mutation_rate, 0.5))
                
                new_pop.append(child)

            population = new_pop

        return best

    def export_excel(self, schedule):
        df = pd.DataFrame(schedule)
        # Thêm cột timeslot_detail
        df['timeslot_detail'] = df['timeslot'].apply(get_timeslot_detail)
        # Sắp xếp lại thứ tự cột và bỏ cột timeslot
        columns = ['course_id', 'course_name', 'subject_code', 'section', 'teacher', 'room', 'timeslot_detail']
        df = df[columns]
        filename = f"schedule_50classes_{pd.Timestamp.now().strftime('%H%M%S')}.xlsx"
        df.to_excel(filename, index=False)
        print(f"✅ Đã lưu: {filename}")


import random

def crossover(a, b):
    """
    Uniform crossover thông minh: 
    - Ưu tiên timeslot từ parent tốt hơn
    - Tránh conflicts khi có thể
    """
    child = []
    
    for i in range(len(a)):
        class_a = a[i]
        class_b = b[i]
        
        # Tạo bản copy của class
        child_class = class_a.copy()
        
        # 70% lấy từ parent a, 30% từ parent b (uniform crossover)
        if random.random() < 0.7:
            child_class['timeslot'] = class_a['timeslot']
        else:
            child_class['timeslot'] = class_b['timeslot']
        
        child.append(child_class)
    
    # Local optimization: Sửa một số conflicts ngẫu nhiên
    for _ in range(min(3, len(child) // 10)):  # Sửa tối đa 3 conflicts
        fix_random_conflict(child)
    
    return child

def fix_random_conflict(schedule):
    """
    Tìm và sửa 1 conflict ngẫu nhiên trong schedule
    """
    from genetic_algorithm import generate_preferred_timeslot, generate_random_room
    
    conflicts = []
    
    # Tìm tất cả conflicts
    for i in range(len(schedule)):
        for j in range(i+1, len(schedule)):
            a, b = schedule[i], schedule[j]
            if ((a['room'] == b['room'] and a['timeslot'] == b['timeslot']) or
                (a['teacher'] == b['teacher'] and a['timeslot'] == b['timeslot'])):
                conflicts.append((i, j))
    
    # Nếu có conflict, sửa ngẫu nhiên 1 cái
    if conflicts:
        i, j = random.choice(conflicts)
        # Thay đổi timeslot hoặc room của một trong hai class conflict
        target_idx = random.choice([i, j])
        
        # 60% thay timeslot, 40% thay room
        if random.random() < 0.6:
            schedule[target_idx]['timeslot'] = generate_preferred_timeslot()
        else:
            schedule[target_idx]['room'] = generate_random_room()

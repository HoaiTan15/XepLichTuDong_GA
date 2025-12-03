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
     FIX: Tìm và sửa 1 conflict ngẫu nhiên ĐÚNG CÁCH
    - Thử nhiều lần để tìm timeslot/room không conflict
    - Giảm thiểu việc tạo conflict mới
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
        
        #  FIX: Thử tối đa 20 lần để tìm giá trị không conflict
        max_attempts = 20
        original_timeslot = schedule[target_idx]['timeslot']
        original_room = schedule[target_idx]['room']
        
        for attempt in range(max_attempts):
            # 60% thay timeslot, 40% thay room
            if random.random() < 0.6:
                new_timeslot = generate_preferred_timeslot()
                
                #  Kiểm tra xem timeslot mới có tạo conflict không
                has_conflict = False
                for k in range(len(schedule)):
                    if k != target_idx:
                        other = schedule[k]
                        # Check room conflict với timeslot mới
                        if other['room'] == schedule[target_idx]['room'] and other['timeslot'] == new_timeslot:
                            has_conflict = True
                            break
                        # Check teacher conflict với timeslot mới
                        if other['teacher'] == schedule[target_idx]['teacher'] and other['timeslot'] == new_timeslot:
                            has_conflict = True
                            break
                
                # Nếu không conflict, áp dụng
                if not has_conflict:
                    schedule[target_idx]['timeslot'] = new_timeslot
                    return  #  Thoát ngay khi fix thành công
                    
            else:
                new_room = generate_random_room()
                
                #  Kiểm tra xem room mới có tạo conflict không
                has_conflict = False
                for k in range(len(schedule)):
                    if k != target_idx:
                        other = schedule[k]
                        # Check room conflict với timeslot hiện tại
                        if other['room'] == new_room and other['timeslot'] == schedule[target_idx]['timeslot']:
                            has_conflict = True
                            break
                
                # Nếu không conflict, áp dụng
                if not has_conflict:
                    schedule[target_idx]['room'] = new_room
                    return  #  Thoát ngay khi fix thành công
        
        #  Nếu thử hết 20 lần vẫn không tìm được → giữ nguyên giá trị cũ
        # (tránh tạo conflict mới)
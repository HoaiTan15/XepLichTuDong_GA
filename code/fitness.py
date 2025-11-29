
def fitness_score(schedule):
    """
    Hàm fitness cải thiện để tránh xung đột và phân bổ đều timeslot
    Trả về giá trị gần 1.0 cho chất lượng tốt nhất
    """
    conflicts = 0
    total_classes = len(schedule)
    evening_classes = 0
    sunday_classes = 0
    
    # 1. Đếm xung đột cơ bản
    room_conflicts = 0
    teacher_conflicts = 0
    
    for i in range(total_classes):
        for j in range(i+1, total_classes):
            a = schedule[i]
            b = schedule[j]

            # Room conflict
            if a['room'] == b['room'] and a['timeslot'] == b['timeslot']:
                room_conflicts += 1
                conflicts += 1

            # Teacher conflict
            if a['teacher'] == b['teacher'] and a['timeslot'] == b['timeslot']:
                teacher_conflicts += 1
                conflicts += 1

    # 2. Đếm lớp buổi tối và Chủ nhật
    for cls in schedule:
        ts = cls['timeslot']
        # Tính ngày trong tuần (0-6: Thứ 2 - Chủ nhật)
        day_index = (ts - 1) // 5
        # Tính buổi trong ngày (1-5)
        session_in_day = ((ts - 1) % 5) + 1
        
        # Đếm buổi tối (session 5) - không áp dụng cho Chủ nhật
        if session_in_day == 5 and day_index < 6:  # Buổi tối Thứ 2-7
            evening_classes += 1
        
        # Đếm Chủ nhật (ngày thứ 6, index = 6)
        if day_index == 6:  # Chủ nhật
            sunday_classes += 1

    # 3. Tính fitness score (gần 1.0 cho kết quả hoàn hảo)
    # Công thức: fitness = 1 / (1 + total_penalty)
    evening_penalty = evening_classes * 0.05  # Penalty nhẹ cho buổi tối
    sunday_penalty = sunday_classes * 0.1     # Penalty nặng hơn cho Chủ nhật
    conflict_penalty = conflicts * 10         # Penalty rất nặng cho xung đột
    
    total_penalty = conflict_penalty + evening_penalty + sunday_penalty
    
    # Đảm bảo fitness luôn > 0 và gần 1.0 khi hoàn hảo
    fitness = 1.0 / (1.0 + total_penalty)
    
    return fitness

def fitness_score(schedule):
    """Tính điểm fitness và trả thêm thông tin phạt chi tiết.

    Returns
    -------
    fitness : float
        Điểm fitness (0 < fitness <= 1).
    info : dict
        Thông tin chi tiết: số conflict, penalty từng loại, tổng penalty.
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

    # Cân bằng lại penalty weights
    # Với 50 lớp: tối đa ~1225 cặp (50*49/2), conflict thực tế thường < 50

    # Penalty tuyệt đối (không phụ thuộc số lượng lớp)
    conflict_penalty = conflicts * 5.0
    evening_penalty = evening_classes * 0.3
    sunday_penalty = sunday_classes * 0.5

    # Penalty tương đối (phụ thuộc tỷ lệ %)
    # VD: 10 buổi tối trong 50 lớp = 20% → thêm penalty
    evening_ratio_penalty = (evening_classes / total_classes) * 2.0 if evening_classes > total_classes * 0.15 else 0
    sunday_ratio_penalty = (sunday_classes / total_classes) * 3.0 if sunday_classes > total_classes * 0.05 else 0
    
    total_penalty = (
        conflict_penalty
        + evening_penalty
        + sunday_penalty
        + evening_ratio_penalty
        + sunday_ratio_penalty
    )

    # Đảm bảo fitness luôn > 0 và gần 1.0 khi hoàn hảo
    fitness = 1.0 / (1.0 + total_penalty)

    info = {
        "conflicts": conflicts,
        "room_conflicts": room_conflicts,
        "teacher_conflicts": teacher_conflicts,
        "evening_classes": evening_classes,
        "sunday_classes": sunday_classes,
        "conflict_penalty": conflict_penalty,
        "evening_penalty": evening_penalty,
        "sunday_penalty": sunday_penalty,
        "evening_ratio_penalty": evening_ratio_penalty,
        "sunday_ratio_penalty": sunday_ratio_penalty,
        "total_penalty": total_penalty,
    }

    return fitness, info
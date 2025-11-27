
import pandas as pd
from genetic_algorithm import GeneticAlgorithm

def main():
    # Sử dụng dataset 50 lớp với format phòng đã sửa
    print("📊 Đọc dataset 50 lớp học...")
    df = pd.read_excel("../data/dataset_50_classes_fixed.xlsx", skiprows=1, header=None, dtype=str)
    df.columns = ['course_id', 'course_name', 'subject_code', 'section', 'teacher', 'room']
    
    print(f"   ✅ Đã đọc {len(df)} lớp học")
    print(f"   👨‍🏫 Số giảng viên: {df['teacher'].nunique()}")
    print(f"   🏛️ Số phòng học: {df['room'].nunique()}")
    
    print("\n🧬 Khởi tạo Genetic Algorithm...")
    ga = GeneticAlgorithm(df, population_size=40, generations=100)  # Giảm tham số cho dataset nhỏ hơn
    
    print("⏳ Đang chạy thuật toán...")
    best = ga.run()
    
    print(f"\n🎯 Kết quả:")
    print(f"   Fitness tốt nhất: {best['fitness']:.6f}")
    
    # Tính số xung đột
    conflicts = 0
    schedule = best['schedule']
    for i in range(len(schedule)):
        for j in range(i+1, len(schedule)):
            a, b = schedule[i], schedule[j]
            if (a['room'] == b['room'] and a['timeslot'] == b['timeslot']) or \
               (a['teacher'] == b['teacher'] and a['timeslot'] == b['timeslot']):
                conflicts += 1
    
    print(f"   Số xung đột: {conflicts}")
    print(f"   Tỷ lệ thành công: {((len(df)*(len(df)-1)/2 - conflicts)/(len(df)*(len(df)-1)/2)*100):.2f}%")
    
    print("\n💾 Xuất lịch ra Excel...")
    ga.export_excel(best['schedule'])
    best = ga.run()
    print("Best schedule fitness:", best['fitness'])
    ga.export_excel(best['schedule'])

if __name__ == "__main__":
    main()

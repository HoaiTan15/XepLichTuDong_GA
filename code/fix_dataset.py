"""
Tạo lại dataset 50 lớp với format phòng học đúng
"""
import pandas as pd

def fix_room_format():
    print("🔧 Sửa lại format phòng học...")
    
    # Đọc dataset gốc với dtype=str
    df_full = pd.read_excel("../data/datasetHP.xlsx", skiprows=1, header=None, dtype=str)
    df_full.columns = ['course_id', 'course_name', 'subject_code', 'section', 'teacher', 'room']
    
    print("✅ Mẫu phòng học sau khi sửa:")
    print(df_full['room'].head(10).tolist())
    
    # Lấy 50 lớp đầu tiên
    df_small = df_full.head(50).copy()
    
    # Lưu dataset mới với format đúng
    with pd.ExcelWriter("../data/dataset_50_classes_fixed.xlsx", engine='openpyxl') as writer:
        # Sheet header
        header_row = pd.DataFrame([['course_id', 'course_name', 'subject_code', 'section', 'teacher', 'room']])
        header_row.to_excel(writer, sheet_name='Data', index=False, header=False)
        
        # Dữ liệu với format text
        df_small.to_excel(writer, sheet_name='Data', index=False, header=False, startrow=1)
        
        # Format cột room thành text
        worksheet = writer.sheets['Data']
        for row in range(2, len(df_small) + 2):
            cell = worksheet[f'F{row}']  # Cột F là room
            cell.number_format = '@'  # Text format
    
    print(f"✅ Đã tạo dataset mới: ../data/dataset_50_classes_fixed.xlsx")
    print(f"📊 Số lớp: {len(df_small)}")
    print(f"🏛️ Mẫu phòng: {df_small['room'].head(5).tolist()}")

if __name__ == "__main__":
    fix_room_format()
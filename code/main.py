"""
WEB APP - GENETIC ALGORITHM SCHEDULE OPTIMIZER
Giao diện web đơn giản cho thuật toán tối ưu hóa lịch học
"""

from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import pandas as pd
import os
import io
import base64
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from genetic_algorithm import GeneticAlgorithm, get_timeslot_detail
import threading
import time

app = Flask(__name__)
app.secret_key = 'genetic_algorithm_secret_key'

# Global variables để track progress
current_progress = {'status': 'idle', 'progress': 0, 'best_fitness': 0, 'generation': 0}

class ProgressTracker:
    def __init__(self):
        self.reset()
    
    def reset(self):
        global current_progress
        current_progress = {'status': 'idle', 'progress': 0, 'best_fitness': 0, 'generation': 0}
    
    def update(self, generation, max_gen, best_fitness):
        global current_progress
        current_progress = {
            'status': 'running',
            'progress': int((generation / max_gen) * 100),
            'best_fitness': best_fitness,
            'generation': generation
        }

progress_tracker = ProgressTracker()

class WebGeneticAlgorithm(GeneticAlgorithm):
    """GA with web progress tracking"""
    
    def run(self):
        global current_progress
        progress_tracker.reset()
        population = self.create_population()
        best = None
        stagnant_count = 0

        for gen in range(self.generations):
            # Evaluate fitness
            from fitness import fitness_score
            scored = [{"schedule": ind, "fitness": fitness_score(ind)} for ind in population]
            scored.sort(key=lambda x: x['fitness'], reverse=True)

            # Track best solution
            if best is None or scored[0]['fitness'] > best['fitness']:
                best = scored[0].copy()
                stagnant_count = 0
            else:
                stagnant_count += 1
            
            # Update progress
            progress_tracker.update(gen + 1, self.generations, best['fitness'])
            
            # Early stopping cho web app nếu quá lâu không cải thiện (15 giây)
            if stagnant_count > 15:  # Nhanh chóng nhờ Early Stopping
                current_progress['progress'] = 100  # Đảm bảo progress = 100% khi hoàn thành
                current_progress['status'] = 'completed'
                return best

            # Elitism: Giữ lại top tốt nhất
            elite_size = max(5, self.population_size // 8)  # Tăng elite size
            new_pop = [s['schedule'] for s in scored[:elite_size]]

            # Generate new population với tournament selection
            while len(new_pop) < self.population_size:
                import random
                from crossover import crossover
                from mutation import mutate
                
                # Tournament selection
                tournament1 = random.sample(scored[:self.population_size//2], min(3, len(scored)))
                tournament2 = random.sample(scored[:self.population_size//2], min(3, len(scored)))
                
                p1 = max(tournament1, key=lambda x: x['fitness'])
                p2 = max(tournament2, key=lambda x: x['fitness'])
                
                child = crossover(p1['schedule'], p2['schedule'])
                
                # Adaptive mutation - tăng dần khi stagnant
                base_rate = 0.08  # Giảm base rate
                adaptive_rate = base_rate + (stagnant_count * 0.015)
                mutation_rate = min(adaptive_rate, 0.35)  # Max 35%
                mutate(child, rate=mutation_rate)
                
                new_pop.append(child)

            population = new_pop
            time.sleep(0.01)  # Small delay for UI updates

        # Đảm bảo progress = 100% khi chạy xong tất cả generations
        current_progress['progress'] = 100
        current_progress['status'] = 'completed'
        return best

@app.route('/')
def index():
    """Trang chủ"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload và xử lý file Excel"""
    if 'file' not in request.files:
        flash('Không có file được chọn!')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('Không có file được chọn!')
        return redirect(url_for('index'))
    
    if file and file.filename.endswith('.xlsx'):
        try:
            # Read the uploaded file với dtype=str để giữ nguyên format
            df = pd.read_excel(file, skiprows=1, header=None, dtype=str)
            df.columns = ['course_id', 'course_name', 'subject_code', 'section', 'teacher']
            
            # Tạo danh sách phòng học available (tự động generate)
            available_rooms = []
            # Tầng A: A101-A110, A201-A210, A301-A310, A401-A410
            for floor in [1, 2, 3, 4]:
                for room_num in range(1, 11):
                    available_rooms.append(f"A{floor}0{room_num}")
            # Tầng B: B101-B110, B201-B210, B301-B310, B401-B410
            for floor in [1, 2, 3, 4]:
                for room_num in range(1, 11):
                    available_rooms.append(f"B{floor}0{room_num}")
            
            # Lưu danh sách phòng để GA sử dụng
            with open('available_rooms.txt', 'w') as f:
                for room in available_rooms:
                    f.write(f"{room}\n")
            
            # Save for processing
            df.to_pickle('temp_data.pkl')
            
            # Show data preview - hiển thị toàn bộ
            data_info = {
                'total_classes': len(df),
                'teachers': df['teacher'].nunique(),
                'rooms': len(available_rooms),  # Số phòng available
                'sample_data': df.to_html(classes='table table-striped table-hover', table_id='dataTable', escape=False)
            }
            
            return render_template('data_preview.html', data_info=data_info)
            
        except Exception as e:
            flash(f'Lỗi đọc file: {str(e)}')
            return redirect(url_for('index'))
    
    else:
        flash('File phải có định dạng .xlsx')
        return redirect(url_for('index'))

@app.route('/run_algorithm', methods=['POST'])
def run_algorithm():
    """Chạy thuật toán GA"""
    try:
        # Load data
        df = pd.read_pickle('temp_data.pkl')
        
        # Get parameters from form - tối ưu cho 50 classes
        population_size = int(request.form.get('population_size', 50))  # Giảm default
        generations = int(request.form.get('generations', 100))  # Giảm default
        
        # Reset progress
        progress_tracker.reset()
        
        # Run GA in background thread
        def run_ga():
            ga = WebGeneticAlgorithm(df, population_size=population_size, generations=generations)
            best = ga.run()
            
            # Save results
            schedule_df = pd.DataFrame(best['schedule'])
            # Thêm cột timeslot_detail
            schedule_df['timeslot_detail'] = schedule_df['timeslot'].apply(get_timeslot_detail)
            # Sắp xếp lại thứ tự cột và bỏ cột timeslot
            columns = ['course_id', 'course_name', 'subject_code', 'section', 'teacher', 'room', 'timeslot_detail']
            schedule_df = schedule_df[columns]
            schedule_df.to_excel('result_schedule.xlsx', index=False)
            
            # Calculate conflicts
            conflict_info = count_conflicts(best['schedule'])
            conflicts = conflict_info['total']
            
            # Đếm số lớp buổi tối và Chủ nhật
            evening_classes = 0
            sunday_classes = 0
            for cls in best['schedule']:
                ts = cls['timeslot']
                day_index = (ts - 1) // 5
                session_in_day = ((ts - 1) % 5) + 1
                
                # Buổi tối (session 5, Thứ 2-7)
                if session_in_day == 5 and day_index < 6:
                    evening_classes += 1
                
                # Chủ nhật (ngày index = 6)
                if day_index == 6:
                    sunday_classes += 1
            
            result = {
                'fitness': best['fitness'],
                'conflicts': conflicts,
                'room_conflicts': conflict_info['room_conflicts'],
                'teacher_conflicts': conflict_info['teacher_conflicts'],
                'evening_classes': evening_classes,
                'sunday_classes': sunday_classes,
                'success_rate': ((len(df)*(len(df)-1)/2 - conflicts)/(len(df)*(len(df)-1)/2)*100)
            }
            
            with open('result_info.txt', 'w') as f:
                f.write(f"{result['fitness']},{result['conflicts']},{result['success_rate']},{result['room_conflicts']},{result['teacher_conflicts']},{result['evening_classes']},{result['sunday_classes']}")
        
        # Start background thread
        thread = threading.Thread(target=run_ga)
        thread.start()
        
        return render_template('running.html')
        
    except Exception as e:
        flash(f'Lỗi chạy thuật toán: {str(e)}')
        return redirect(url_for('index'))

@app.route('/progress')
def get_progress():
    """API endpoint để lấy tiến độ"""
    return current_progress

@app.route('/results')
def show_results():
    """Hiển thị kết quả"""
    try:
        # Read results
        with open('result_info.txt', 'r') as f:
            result_data = f.read().strip().split(',')
            fitness = result_data[0]
            conflicts = result_data[1] 
            success_rate = result_data[2]
            room_conflicts = result_data[3] if len(result_data) > 3 else "0"
            teacher_conflicts = result_data[4] if len(result_data) > 4 else "0"
            evening_classes = result_data[5] if len(result_data) > 5 else "0"
            sunday_classes = result_data[6] if len(result_data) > 6 else "0"
        
        # Read schedule
        schedule_df = pd.read_excel('result_schedule.xlsx')
        # Đảm bảo có cột timeslot_detail và không có cột timeslot
        if 'timeslot' in schedule_df.columns and 'timeslot_detail' not in schedule_df.columns:
            schedule_df['timeslot_detail'] = schedule_df['timeslot'].apply(get_timeslot_detail)
        
        # Bỏ cột timeslot nếu còn tồn tại
        if 'timeslot' in schedule_df.columns:
            schedule_df = schedule_df.drop('timeslot', axis=1)
        
        # Generate charts (sử dụng timeslot_detail thay vì timeslot)
        chart_url = generate_charts(schedule_df)
        
        results = {
            'fitness': float(fitness),
            'conflicts': int(float(conflicts)),
            'room_conflicts': int(float(room_conflicts)),
            'teacher_conflicts': int(float(teacher_conflicts)),
            'evening_classes': int(float(evening_classes)),
            'sunday_classes': int(float(sunday_classes)),
            'success_rate': float(success_rate),
            'total_classes': len(schedule_df),
            'chart_url': chart_url,
            'schedule_table': schedule_df.to_html(classes='table table-striped table-hover', table_id='resultTable', escape=False)
        }
        
        return render_template('results.html', results=results)
        
    except Exception as e:
        flash(f'Lỗi hiển thị kết quả: {str(e)}')
        return redirect(url_for('index'))

@app.route('/download')
def download_file():
    """Download file kết quả"""
    return send_file('result_schedule.xlsx', as_attachment=True, 
                     download_name='optimized_schedule.xlsx')

def count_conflicts(schedule):
    """
    Đếm và phân loại các xung đột
    Returns: dict với thông tin chi tiết về conflicts
    """
    room_conflicts = 0
    teacher_conflicts = 0
    conflict_details = []
    
    for i in range(len(schedule)):
        for j in range(i+1, len(schedule)):
            a, b = schedule[i], schedule[j]
            
            # Room conflict
            if a['room'] == b['room'] and a['timeslot'] == b['timeslot']:
                room_conflicts += 1
                conflict_details.append({
                    'type': 'Room',
                    'room': a['room'],
                    'timeslot': a['timeslot'],
                    'class1': f"{a['course_name']} ({a['section']})",
                    'class2': f"{b['course_name']} ({b['section']})"
                })
            
            # Teacher conflict  
            if a['teacher'] == b['teacher'] and a['timeslot'] == b['timeslot']:
                teacher_conflicts += 1
                conflict_details.append({
                    'type': 'Teacher',
                    'teacher': a['teacher'],
                    'timeslot': a['timeslot'],
                    'class1': f"{a['course_name']} ({a['section']})",
                    'class2': f"{b['course_name']} ({b['section']})"
                })
    
    return {
        'total': room_conflicts + teacher_conflicts,
        'room_conflicts': room_conflicts,
        'teacher_conflicts': teacher_conflicts,
        'details': conflict_details
    }

def generate_charts(df):
    """Tạo biểu đồ và trả về base64 string"""
    plt.figure(figsize=(14, 10))
    
    # 1. Phân bổ theo ca học (từ timeslot_detail)
    plt.subplot(2, 3, 1)
    if 'timeslot_detail' in df.columns:
        # Trích xuất thông tin ca học từ timeslot_detail
        ca_hoc = df['timeslot_detail'].str.extract(r'- (Sáng|Chiều|Tối) -')[0].value_counts()
        plt.pie(ca_hoc.values, labels=ca_hoc.index, autopct='%1.1f%%', startangle=90,
                colors=['gold', 'lightcoral', 'lightblue'])
        plt.title('Phân bổ theo Ca học')
    else:
        plt.text(0.5, 0.5, 'Không có dữ liệu timeslot_detail', ha='center', va='center')
        plt.title('Phân bổ theo Ca học')
    
    # 2. Room usage
    plt.subplot(2, 3, 2)
    room_counts = df['room'].value_counts()
    plt.hist(room_counts.values, bins=10, color='lightgreen', alpha=0.8, edgecolor='black')
    plt.title('Sử dụng phòng học')
    plt.xlabel('Số lớp/phòng')
    plt.ylabel('Số phòng')
    plt.grid(True, alpha=0.3)
    
    # 3. Teacher workload
    plt.subplot(2, 3, 3)
    teacher_counts = df['teacher'].value_counts().head(10)
    plt.barh(range(len(teacher_counts)), teacher_counts.values, color='orange', alpha=0.8)
    plt.title('Top 10 giảng viên')
    plt.xlabel('Số lớp')
    plt.yticks(range(len(teacher_counts)), [name[:15] + '...' if len(name) > 15 else name for name in teacher_counts.index])
    
    # 4. Thứ trong tuần distribution
    plt.subplot(2, 3, 4)
    if 'timeslot_detail' in df.columns:
        thu_hoc = df['timeslot_detail'].str.extract(r'(Thứ \d+|Chủ nhật)')[0].value_counts()
        plt.bar(range(len(thu_hoc)), thu_hoc.values, color='mediumpurple', alpha=0.8)
        plt.title('Phân bổ theo Thứ')
        plt.xlabel('Thứ')
        plt.ylabel('Số lớp')
        plt.xticks(range(len(thu_hoc)), thu_hoc.index, rotation=45)
        plt.grid(True, alpha=0.3)
    else:
        plt.text(0.5, 0.5, 'Không có dữ liệu', ha='center', va='center')
        plt.title('Phân bổ theo Thứ')
    
    # 5. Phân bổ chi tiết theo timeslot_detail (top 10)
    plt.subplot(2, 3, 5)
    if 'timeslot_detail' in df.columns:
        timeslot_detail_counts = df['timeslot_detail'].value_counts().head(10)
        plt.barh(range(len(timeslot_detail_counts)), timeslot_detail_counts.values, color='skyblue', alpha=0.8)
        plt.title('Top 10 Timeslot')
        plt.xlabel('Số lớp')
        plt.yticks(range(len(timeslot_detail_counts)), 
                  [detail[:20] + '...' if len(detail) > 20 else detail for detail in timeslot_detail_counts.index])
    else:
        plt.text(0.5, 0.5, 'Không có dữ liệu', ha='center', va='center')
        plt.title('Top 10 Timeslot')
    
    # 6. Phân bổ buổi tối và Chủ nhật
    plt.subplot(2, 3, 6)
    if 'timeslot_detail' in df.columns:
        special_counts = {}
        for detail in df['timeslot_detail']:
            if 'Tối' in detail:
                special_counts['Buổi tối'] = special_counts.get('Buổi tối', 0) + 1
            elif 'Chủ nhật' in detail:
                special_counts['Chủ nhật'] = special_counts.get('Chủ nhật', 0) + 1
            else:
                special_counts['Giờ hành chính'] = special_counts.get('Giờ hành chính', 0) + 1
        
        if special_counts:
            plt.pie(special_counts.values(), labels=special_counts.keys(), autopct='%1.1f%%', 
                    startangle=90, colors=['lightgreen', 'lightcoral', 'gold'])
        plt.title('Phân loại đặc biệt')
    else:
        plt.text(0.5, 0.5, 'Không có dữ liệu', ha='center', va='center')
        plt.title('Phân loại đặc biệt')
    
    plt.tight_layout()
    
    # Convert to base64
    img = io.BytesIO()
    plt.savefig(img, format='png', dpi=150, bbox_inches='tight')
    img.seek(0)
    chart_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    return chart_url

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
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
from genetic_algorithm import GeneticAlgorithm
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
        progress_tracker.reset()
        population = self.create_population()
        best = None

        for gen in range(self.generations):
            # Evaluate fitness
            from fitness import fitness_score
            scored = [{"schedule": ind, "fitness": fitness_score(ind)} for ind in population]
            scored.sort(key=lambda x: x['fitness'], reverse=True)

            if best is None or scored[0]['fitness'] > best['fitness']:
                best = scored[0].copy()
            
            # Update progress
            progress_tracker.update(gen, self.generations, best['fitness'])
            
            # Selection
            survivors = scored[:20]
            new_pop = [s['schedule'] for s in survivors]

            # Generate new population
            while len(new_pop) < self.population_size:
                import random
                from crossover import crossover
                from mutation import mutate
                
                p1, p2 = random.sample(survivors, 2)
                child = crossover(p1['schedule'], p2['schedule'])
                mutate(child)
                new_pop.append(child)

            population = new_pop
            time.sleep(0.01)  # Small delay for UI updates

        global current_progress
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
            df.columns = ['course_id', 'course_name', 'subject_code', 'section', 'teacher', 'room']
            
            # Save for processing
            df.to_pickle('temp_data.pkl')
            
            # Show data preview
            data_info = {
                'total_classes': len(df),
                'teachers': df['teacher'].nunique(),
                'rooms': df['room'].nunique(),
                'sample_data': df.head(10).to_html(classes='table table-striped', table_id='dataTable')
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
        
        # Get parameters from form
        population_size = int(request.form.get('population_size', 50))
        generations = int(request.form.get('generations', 100))
        
        # Reset progress
        progress_tracker.reset()
        
        # Run GA in background thread
        def run_ga():
            ga = WebGeneticAlgorithm(df, population_size=population_size, generations=generations)
            best = ga.run()
            
            # Save results
            schedule_df = pd.DataFrame(best['schedule'])
            schedule_df.to_excel('result_schedule.xlsx', index=False)
            
            # Calculate conflicts
            conflicts = count_conflicts(best['schedule'])
            
            result = {
                'fitness': best['fitness'],
                'conflicts': conflicts,
                'success_rate': ((len(df)*(len(df)-1)/2 - conflicts)/(len(df)*(len(df)-1)/2)*100)
            }
            
            with open('result_info.txt', 'w') as f:
                f.write(f"{result['fitness']},{result['conflicts']},{result['success_rate']}")
        
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
            fitness, conflicts, success_rate = f.read().strip().split(',')
        
        # Read schedule
        schedule_df = pd.read_excel('result_schedule.xlsx')
        
        # Generate charts
        chart_url = generate_charts(schedule_df)
        
        results = {
            'fitness': float(fitness),
            'conflicts': int(float(conflicts)),
            'success_rate': float(success_rate),
            'total_classes': len(schedule_df),
            'chart_url': chart_url,
            'schedule_table': schedule_df.head(20).to_html(classes='table table-striped', table_id='resultTable')
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
    """Đếm số xung đột"""
    conflicts = 0
    for i in range(len(schedule)):
        for j in range(i+1, len(schedule)):
            a, b = schedule[i], schedule[j]
            if (a['room'] == b['room'] and a['timeslot'] == b['timeslot']) or \
               (a['teacher'] == b['teacher'] and a['timeslot'] == b['timeslot']):
                conflicts += 1
    return conflicts

def generate_charts(df):
    """Tạo biểu đồ và trả về base64 string"""
    plt.figure(figsize=(12, 8))
    
    # 1. Timeslot distribution
    plt.subplot(2, 2, 1)
    timeslot_counts = df['timeslot'].value_counts().sort_index()
    plt.bar(timeslot_counts.index, timeslot_counts.values, color='skyblue', alpha=0.8)
    plt.title('Phân bổ theo Timeslot')
    plt.xlabel('Timeslot')
    plt.ylabel('Số lớp')
    plt.grid(True, alpha=0.3)
    
    # 2. Room usage
    plt.subplot(2, 2, 2)
    room_counts = df['room'].value_counts()
    plt.hist(room_counts.values, bins=10, color='lightgreen', alpha=0.8, edgecolor='black')
    plt.title('Sử dụng phòng học')
    plt.xlabel('Số lớp/phòng')
    plt.ylabel('Số phòng')
    plt.grid(True, alpha=0.3)
    
    # 3. Teacher workload
    plt.subplot(2, 2, 3)
    teacher_counts = df['teacher'].value_counts().head(10)
    plt.barh(range(len(teacher_counts)), teacher_counts.values, color='orange', alpha=0.8)
    plt.title('Top 10 giảng viên')
    plt.xlabel('Số lớp')
    plt.yticks(range(len(teacher_counts)), [name[:15] + '...' if len(name) > 15 else name for name in teacher_counts.index])
    
    # 4. Timeslot pie chart
    plt.subplot(2, 2, 4)
    top_timeslots = timeslot_counts.head(8)
    plt.pie(top_timeslots.values, labels=[f'TS{ts}' for ts in top_timeslots.index], 
            autopct='%1.1f%%', startangle=90)
    plt.title('Top 8 Timeslot')
    
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
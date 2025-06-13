from flask import Flask, request, render_template, send_from_directory, redirect
from werkzeug.utils import secure_filename
import os
import mysql.connector

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configure MySQL
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Chetana123@',
    'database': 'student_projects'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/')
def form():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    student_name = request.form['student_name']
    course_name = request.form['course_name']
    topic_name = request.form['topic_name']
    file = request.files['project_folder']

    if file:
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], course_name, student_name, topic_name)
        os.makedirs(save_path, exist_ok=True)
        file_path = os.path.join(save_path, filename)
        file.save(file_path)

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get student ID
        cursor.execute("SELECT id FROM students WHERE name=%s AND course=%s", (student_name, course_name))
        result = cursor.fetchone()

        if result:
            student_id = result[0]
        else:
            cursor.execute("INSERT INTO students (name, course) VALUES (%s, %s)", (student_name, course_name))
            student_id = cursor.lastrowid

        # Insert submission
        cursor.execute("INSERT INTO submissions (student_id, topic, file_name, file_path) VALUES (%s, %s, %s, %s)",
                       (student_id, topic_name, filename, file_path))
        conn.commit()
        conn.close()

        return "File uploaded successfully!"
    return "Failed to upload."

@app.route('/admin')
def admin_panel():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.name AS student, s.course, sub.topic, sub.file_name, sub.file_path
        FROM students s
        JOIN submissions sub ON s.id = sub.student_id
        WHERE sub.file_name IS NOT NULL
    """)
    submissions = cursor.fetchall()

    # Format path for downloading
    for sub in submissions:
        full_path = sub['file_path']
        rel_path = full_path.replace(app.config['UPLOAD_FOLDER'], '').strip(os.sep)
        sub['filepath'] = '/download/' + rel_path.replace('\\', '/')

    conn.close()
    return render_template('admin.html', submissions=submissions)

@app.route('/download/<path:filename>')
def download_file(filename):
    full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    directory = os.path.dirname(full_path)
    file = os.path.basename(full_path)
    return send_from_directory(directory, file, as_attachment=True)

@app.route('/admin/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['student_name']
        course = request.form['course_name']
        topics = ['Python', 'Excel', 'PowerBI', 'SQL', 'Python Packages', 'Data Analysis Complete', 'ML', 'DL', 'NLP', 'AI']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO students (name, course) VALUES (%s, %s)", (name, course))
        student_id = cursor.lastrowid

        for topic in topics:
            cursor.execute("INSERT INTO submissions (student_id, topic, file_name, file_path) VALUES (%s, %s, NULL, NULL)", (student_id, topic))

        conn.commit()
        conn.close()
        return redirect('/admin')

    return render_template('add_student.html')

if __name__ == '__main__':
   
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

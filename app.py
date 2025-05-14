from flask import Flask, request, render_template,send_from_directory,redirect
import os
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def form():
    return render_template('index.html')  # The HTML file above

@app.route('/upload', methods=['POST'])
def upload():
    student_name = request.form['student_name']
    course_name = request.form['course_name']
    topic_name = request.form['topic_name']
    file = request.files['project_folder']

    if file:
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], course_name, student_name,topic_name, )
        os.makedirs(save_path, exist_ok=True)
        file.save(os.path.join(save_path, filename))
        return "File uploaded successfully!"
    return "Failed to upload."
@app.route('/admin')
def admin_panel():
    submissions = []

    for course in os.listdir(UPLOAD_FOLDER):
        course_path = os.path.join(UPLOAD_FOLDER, course)
        if os.path.isdir(course_path):
            for student in os.listdir(course_path):
                student_path = os.path.join(course_path, student)
                if os.path.isdir(student_path):
                    for topic in os.listdir(student_path):
                        topic_path = os.path.join(student_path, topic)
                        if os.path.isdir(topic_path):
                            for file in os.listdir(topic_path):
                                file_path = os.path.join(topic_path, file)
                                submissions.append({
                                    'student': student,
                                    'course': course,
                                    'topic': topic,
                                    'filename': file,
                                    'filepath': f'/download/{course}/{student}/{topic}/{file}'
                                })

    return render_template('admin.html', submissions=submissions)



@app.route('/download/<course>/<student>/<topic>/<filename>')
def download_file(course, student, topic, filename):
    directory = os.path.join(app.config['UPLOAD_FOLDER'], course, student, topic)
    return send_from_directory(directory, filename, as_attachment=True)


@app.route('/admin/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['student_name']
        course = request.form['course_name']
        topics = ['Python', 'Excel', 'PowerBI', 'SQL', 'Python Packages', 'Data Analysis Complete', 'ML', 'DL', 'NLP', 'AI']

        conn = sqlite3.connect('students.db')
        c = conn.cursor()
        c.execute("INSERT INTO students (name, course) VALUES (?, ?)", (name, course))
        student_id = c.lastrowid

        for topic in topics:
            c.execute("INSERT INTO submissions (student_id, topic, file_name) VALUES (?, ?, NULL)", (student_id, topic))

        conn.commit()
        conn.close()

        return redirect('/admin')

    return render_template('add_student.html')


if __name__ == '__main__':
    app.run(debug=True)

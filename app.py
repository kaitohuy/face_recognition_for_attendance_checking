import time
from datetime import datetime, timedelta
from flask import Flask, Response, jsonify, render_template, request
import cv2
import numpy as np
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

facedetect = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
recognizer = cv2.face.LBPHFaceRecognizer.create()
try:
 recognizer.read("recognizer/trainingdata.yml")
except cv2.error:
 print("Error: Cannot load trainingdata.yml. Please run trainer.py first.")
 exit()

recent_attendances = {}

cam = cv2.VideoCapture(0)
if not cam.isOpened():
 print("Error: Cannot open webcam")
 exit()

@app.route('/')
def index():
 return render_template('index.html')

def getprofile(id):
 conn = sqlite3.connect("sqlite.db")
 cursor = conn.execute("SELECT * FROM STUDENTS WHERE ID = ?", (id,))
 profile = None
 for row in cursor:
     profile = row
 conn.close()
 return profile

def update_attendance(id, is_manual=False):
    try:
        conn = sqlite3.connect("sqlite.db")
        cursor = conn.execute("SELECT Attendance, Name, Msv FROM STUDENTS WHERE ID = ?", (id,))
        result = cursor.fetchone()
        current_attendance, name, msv = result[0], result[1], result[2]
        if current_attendance == 0:
            # Lưu Timestamp theo UTC+7
            vn_time = datetime.utcnow() + timedelta(hours=7)
            timestamp = vn_time.strftime('%Y-%m-%d %H:%M:%S')
            conn.execute("UPDATE STUDENTS SET Attendance = 1 WHERE ID = ?", (id,))
            conn.execute("INSERT INTO AttendanceHistory (StudentID, Name, Msv, Timestamp) VALUES (?, ?, ?, ?)",
                        (id, name, msv, timestamp))
            conn.commit()

            recent_attendances[id] = {
                "name": name,
                "msv": msv,
                "timestamp": time.time(),
                "manual": is_manual
            }
        conn.close()
        return current_attendance == 0
    except sqlite3.Error as e:
        print(f"Database error in update_attendance: {e}")
        return False

def gen_frames():
 while True:
     ret, img = cam.read()
     img = cv2.flip(img, 1)
     if not ret:
         print("Error: Failed to capture image")
         break
     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
     faces = facedetect.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
     for (x, y, w, h) in faces:
         face = gray[y:y+h, x:x+w]
         face = cv2.equalizeHist(face)
         try:
             id, conf = recognizer.predict(face)
             if conf < 70:
                 profile = getprofile(id)
                 if profile:
                     profile = getprofile(id)
                     if profile and id not in recent_attendances:
                         if update_attendance(id):
                             recent_attendances[id] = {
                                 "name": profile[1],
                                 "msv": profile[2],
                                 "timestamp": time.time(),
                                 "manual": False
                             }
                     cv2.putText(img, f"Name: {profile[1]}", (x, y + h + 25), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 127), 2)
         except Exception as e:
             print(f"Error in prediction: {e}")
         cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
     ret, buffer = cv2.imencode('.jpg', img)
     if not ret:
         print("Error: Failed to encode image")
         continue
     frame = buffer.tobytes()
     yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
 return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/students')
def get_students():
    filter_type = request.args.get('filter', 'all')
    try:
        conn = sqlite3.connect("sqlite.db")
        if filter_type == 'present':
            cursor = conn.execute("SELECT ID, Name, Msv, Lop, Age, Attendance FROM STUDENTS WHERE Attendance = 1")
        elif filter_type == 'absent':
            cursor = conn.execute("SELECT ID, Name, Msv, Lop, Age, Attendance FROM STUDENTS WHERE Attendance = 0")
        else:
            cursor = conn.execute("SELECT ID, Name, Msv, Lop, Age, Attendance FROM STUDENTS")
        students = [{"id": row[0], "name": row[1], "msv": row[2], "lop": row[3], "age": row[4], "attendance": row[5]} for row in cursor]
        conn.close()
        return jsonify(students)
    except sqlite3.Error as e:
        print(f"Database error in get_students: {e}")
        return jsonify({"error": "Failed to fetch students"}), 500

@app.route('/attendance_stats')
def attendance_stats():
    try:
        conn = sqlite3.connect("sqlite.db")
        cursor = conn.execute("SELECT COUNT(*) FROM STUDENTS")
        total = cursor.fetchone()[0]
        cursor = conn.execute("SELECT COUNT(*) FROM STUDENTS WHERE Attendance = 1")
        present = cursor.fetchone()[0]
        absent = total - present
        conn.close()
        return jsonify({"total": total, "present": present, "absent": absent})
    except sqlite3.Error as e:
        print(f"Database error in attendance_stats: {e}")
        return jsonify({"error": "Failed to fetch stats"}), 500

@app.route('/attendance_history')
def attendance_history():
    date_filter = request.args.get('date', '')
    try:
        conn = sqlite3.connect("sqlite.db")
        if date_filter:
            cursor = conn.execute(
                "SELECT ID, StudentID, Name, Msv, Timestamp FROM AttendanceHistory WHERE DATE(Timestamp) = ?",
                (date_filter,)
            )
        else:
            cursor = conn.execute("SELECT ID, StudentID, Name, Msv, Timestamp FROM AttendanceHistory")
        history = [
            {"id": row[0], "student_id": row[1], "name": row[2], "msv": row[3], "timestamp": row[4]}
            for row in cursor
        ]
        conn.close()
        return jsonify(history)
    except sqlite3.Error as e:
        print(f"Database error in attendance_history: {e}")
        return jsonify({"error": "Failed to fetch attendance history"}), 500

@app.route('/attendance_notification')
def attendance_notification():

    current_time = time.time()
    for id in list(recent_attendances.keys()):
        if current_time - recent_attendances[id]["timestamp"] > 2:
            del recent_attendances[id]
    return jsonify(list(recent_attendances.values()))

@app.route('/reset_attendance_history', methods=['POST'])
def reset_attendance_history():
    conn = sqlite3.connect("sqlite.db")
    conn.execute("DELETE FROM AttendanceHistory")
    conn.commit()
    conn.close()
    return jsonify({"message": "Attendance history reset successfully"})

@app.route('/reset_attendance', methods=['POST'])
def reset_attendance():
    try:
        conn = sqlite3.connect("sqlite.db")
        conn.execute("UPDATE STUDENTS SET Attendance = 0")
        conn.commit()
        conn.close()
        recent_attendances.clear()
        return jsonify({"message": "Attendance reset successfully"})
    except sqlite3.Error as e:
        print(f"Database error in reset_attendance: {e}")
        return jsonify({"error": "Failed to reset attendance"}), 500

@app.route('/manual_attendance', methods=['POST'])
def manual_attendance():
    data = request.get_json()
    student_id = data.get('student_id')
    checked = data.get('checked')
    try:
        conn = sqlite3.connect("sqlite.db")
        if checked:
            success = update_attendance(student_id, is_manual=True)
            if success:
                conn.close()
                return jsonify({"message": "Manual attendance recorded successfully"})
            else:
                conn.close()
                return jsonify({"error": "Student already marked present or not found"}), 400
        else:
            conn.execute("UPDATE STUDENTS SET Attendance = 0 WHERE ID = ?", (student_id,))
            conn.commit()
            conn.close()
            if student_id in recent_attendances:
                del recent_attendances[student_id]
            return jsonify({"message": "Manual attendance cleared successfully"})
    except sqlite3.Error as e:
        print(f"Database error in manual_attendance: {e}")
        return jsonify({"error": "Failed to update manual attendance"}), 500

@app.route('/favicon.ico')
def favicon():
 return '', 204

if __name__ == '__main__':
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    finally:
        cam.release()

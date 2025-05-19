import cv2
import numpy as np
import sqlite3
import os

faceDetect = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
cam = cv2.VideoCapture(0)

if not cam.isOpened():
    print("Error: Cannot open webcam")
    exit()


def insert_student(name, msv, lop, age):
    # Kết nối cơ sở dữ liệu
    conn = sqlite3.connect("sqlite.db")

    # Chèn bản ghi mới, không cung cấp ID (tự động tăng)
    conn.execute("INSERT INTO STUDENTS (Name, Msv, Lop, Age) VALUES (?, ?, ?, ?)", (name, msv, lop, age))
    conn.commit()

    # Lấy ID của bản ghi vừa chèn
    cursor = conn.execute("SELECT last_insert_rowid()")
    new_id = cursor.fetchone()[0]

    conn.close()
    return new_id


# Nhập thông tin người dùng (không cần ID)
try:
    name = input('Enter user name: ').strip()
    msv = input('Enter user msv: ').strip()
    lop = input('Enter user lop: ').strip()
    age = int(input('Enter user age: ').strip())

    # Kiểm tra đầu vào
    if not name or not msv or not lop:
        print("Error: Name, MSV, and Lop cannot be empty")
        cam.release()
        exit()
    if age <= 0:
        print("Error: Age must be a positive number")
        cam.release()
        exit()
except ValueError:
    print("Error: Age must be a number")
    cam.release()
    exit()

# Chèn sinh viên và lấy ID mới
new_id = insert_student(name, msv, lop, age)
print(f"New student added with ID: {new_id}")

# Tạo thư mục dataset nếu chưa tồn tại
if not os.path.exists("dataset"):
    os.makedirs("dataset")

# Thu thập ảnh khuôn mặt
sampleNum = 0
while True:
    ret, img = cam.read()
    if not ret:
        print("Error: Failed to capture image")
        break
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceDetect.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    for (x, y, w, h) in faces:
        sampleNum += 1
        # Cân bằng histogram và lưu ảnh
        face = gray[y:y + h, x:x + w]
        face = cv2.equalizeHist(face)
        cv2.imwrite(f"dataset/user.{new_id}.{sampleNum}.jpg", face)
        # Vẽ khung quanh khuôn mặt
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.waitKey(100)
    cv2.imshow("Face", img)
    cv2.waitKey(1)
    if sampleNum >= 100:
        print(f"Collected {sampleNum} images for user ID {new_id}")
        break

cam.release()
cv2.destroyAllWindows()
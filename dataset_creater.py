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
    conn = sqlite3.connect("sqlite.db")

    conn.execute("INSERT INTO STUDENTS (Name, Msv, Lop, Age) VALUES (?, ?, ?, ?)", (name, msv, lop, age))
    conn.commit()

    cursor = conn.execute("SELECT last_insert_rowid()")
    new_id = cursor.fetchone()[0]

    conn.close()
    return new_id

try:
    name = input('Enter user name: ').strip()
    msv = input('Enter user msv: ').strip()
    lop = input('Enter user lop: ').strip()
    age = int(input('Enter user age: ').strip())

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

new_id = insert_student(name, msv, lop, age)
print(f"New student added with ID: {new_id}")

if not os.path.exists("dataset"):
    os.makedirs("dataset")

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
        face = gray[y:y + h, x:x + w]
        face = cv2.equalizeHist(face)
        cv2.imwrite(f"dataset/user.{new_id}.{sampleNum}.jpg", face)
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.waitKey(100)
    cv2.imshow("Face", img)
    cv2.waitKey(1)
    if sampleNum >= 100:
        print(f"Collected {sampleNum} images for user ID {new_id}")
        break

cam.release()
cv2.destroyAllWindows()
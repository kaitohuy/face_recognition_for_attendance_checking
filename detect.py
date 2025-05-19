import cv2
import numpy as np
import sqlite3

facedetect = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
cam = cv2.VideoCapture(0)

if not cam.isOpened():
    print("Error: Cannot open webcam")
    exit()

recognizer = cv2.face.LBPHFaceRecognizer.create()
try:
    recognizer.read("recognizer/trainingdata.yml")
except cv2.error:
    print("Error: Cannot load trainingdata.yml. Please run trainer.py first.")
    exit()

def getprofile(id):
    conn = sqlite3.connect("sqlite.db")
    cmd = "SELECT * FROM STUDENTS WHERE ID = ?"
    cursor = conn.execute(cmd, (id,))
    profile = None
    for row in cursor:
        profile = row
    conn.close()
    return profile

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
        face = cv2.equalizeHist(face)  # Cân bằng histogram cho vùng khuôn mặt
        id, conf = recognizer.predict(face)
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        if conf < 80:  # Ngưỡng độ tin cậy
            profile = getprofile(id)
            if profile:
                cv2.putText(img, f"Name: {profile[0]}", (x-w//2 + 40, y + h + 25), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 127), 2)
                cv2.putText(img, f"Msv: {profile[1]}", (x-w//2 + 40, y + h + 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 127), 2)
                cv2.putText(img, f"Lop: {profile[2]}", (x-w//2 + 40, y + h + 75), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 127), 2)
                cv2.putText(img, f"Age: {profile[3]}", (x-w//2 + 40, y + h + 100), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 127), 2)
            else:
                cv2.putText(img, "Unknown", (x, y + h + 30), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
        else:
            cv2.putText(img, "Unknown", (x, y + h + 30), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
    cv2.imshow("FACE", img)
    if cv2.waitKey(1) == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()

Hệ thống Điểm danh bằng Nhận diện Khuôn mặt

Hệ thống điểm danh tự động sử dụng nhận diện khuôn mặt, phát triển cho PTIT. Dùng OpenCV, Flask, SQLite, và Tailwind CSS để nhận diện khuôn mặt qua webcam, quản lý điểm danh, và hiển thị giao diện web.

Tải Dự án:

git clone https://github.com/kaitohuy/face_recognition_for_attendance_checking.git

cd face_recognition_for_attendance_checking

Cài Thư viện:

pip install opencv-python opencv-contrib-python numpy flask flask-cors

Chuẩn bị Dữ liệu:

Chạy để thu thập ảnh khuôn mặt:python dataset_creater.py

Nhập thông tin sinh viên

Huấn luyện mô hình:python trainer.py

Chạy Hệ thống

Khởi động Server:python app.py


Truy cập Giao diện:

Local: http://localhost:5000

Mạng: http://192.168.66.234:5000 (cùng Wi-Fi).


Sử dụng:
Xem video feed nhận diện khuôn mặt.
Quản lý danh sách sinh viên, điểm danh thủ công, xem lịch sử.

📹 [Xem video demo tại đây](https://drive.google.com/file/d/12oychTGTyRgtqm_l_4TSEGhZWIx9YKFJ/view?usp=sharing)


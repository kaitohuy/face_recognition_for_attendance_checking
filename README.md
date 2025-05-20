Được chứ! Đây là bản đầy đủ đã gộp lại — bạn chỉ cần **copy toàn bộ và dán vào file `README.md`** là xong:


# 🎓 Hệ thống Điểm danh bằng Nhận diện Khuôn mặt

Hệ thống điểm danh tự động sử dụng nhận diện khuôn mặt, phát triển cho **PTIT**. Ứng dụng sử dụng **OpenCV**, **Flask**, **SQLite**, và **Tailwind CSS** để:

- Nhận diện khuôn mặt qua webcam
- Quản lý điểm danh sinh viên
- Hiển thị giao diện web thân thiện

---

## 🚀 Tải Dự án
```bash
git clone https://github.com/kaitohuy/face_recognition_for_attendance_checking.git
cd face_recognition_for_attendance_checking


## 🧪 Cài Đặt Thư Viện

```bash
pip install opencv-python opencv-contrib-python numpy flask flask-cors
```

---

## 📸 Chuẩn Bị Dữ Liệu

1. **Thu thập ảnh khuôn mặt:**

   ```bash
   python dataset_creater.py
   ```

2. **Nhập thông tin sinh viên (theo yêu cầu của chương trình)**

3. **Huấn luyện mô hình:**

   ```bash
   python trainer.py
   ```

---

## ▶️ Chạy Hệ thống

Khởi động server:

```bash
python app.py
```

---

## 🌐 Truy Cập Giao Diện

* **Local:** [http://localhost:5000](http://localhost:5000)
* **Trong mạng LAN:** `http://192.168.66.234:5000` (các thiết bị cùng Wi-Fi)

---

## 📚 Tính Năng

* 🎥 Xem video feed và nhận diện khuôn mặt trực tiếp từ webcam
* 👨‍🎓 Quản lý danh sách sinh viên
* 📝 Điểm danh tự động hoặc thủ công
* 📅 Xem lịch sử điểm danh

---

## 📹 Demo

👉 [Xem video demo tại đây](https://drive.google.com/file/d/12oychTGTyRgtqm_l_4TSEGhZWIx9YKFJ/view?usp=sharing)

---

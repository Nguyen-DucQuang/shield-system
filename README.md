# AI Shield System (Iron Dome Demo)

## Gioi thieu
AI Shield System la mo phong he thong phong thu don gian:
- Nhan anh tu camera IP
- Phat hien muc tieu bang YOLOv8
- Theo doi muc tieu bang OpenCV tracker
- Du doan vi tri tuong lai va tu dong phong ten lua trong mo phong
- Hien thi tat ca tren giao dien Tkinter

Du an mang tinh hoc tap/mo phong, khong phai he thong vu khi thuc te.

## Cau truc du an
- `main.py`: Diem vao chinh, khoi tao cac module va chay GUI
- `config.py`: Cau hinh camera, vung bao ve, tham so giao dien
- `gui_app.py`: Giao dien Tkinter, luong camera, ve HUD va dieu khien
- `detector.py`: Phat hien doi tuong voi YOLOv8
- `tracker.py`: Theo doi doi tuong va du doan vi tri
- `missile_sim.py`: Mo phong ten lua va hieu ung no

## Yeu cau moi truong
- Windows (khuyen nghi)
- Python 3.10+
- Webcam/IP Webcam stream URL

## Cai dat
### 1. Tao va kich hoat virtual environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Cai dependency
```powershell
python -m pip install --upgrade pip
python -m pip install numpy opencv-python pillow ultralytics
```

## Cau hinh camera
Mo file `config.py` va sua:
```python
CAMERA_URL = "http://<dien-thoai-ip>:8080/video"
```

Vi du:
```python
CAMERA_URL = "http://192.168.1.10:8080/video"
```

Neu ban dung nguon camera khac, hay thay URL tuong ung.

## Cach chay
Tu thu muc du an:
```powershell
.\.venv\Scripts\python.exe .\main.py
```

## Luong su dung
1. Mo app IP Webcam tren dien thoai va Start Server
2. Chay ung dung
3. Bam "Ket noi Camera"
4. Bam "Bat dau theo doi"
5. (Tuy chon) Bat "Tu dong khai hoa"

## Luu y ky thuat
- Lan dau chay YOLO co the tai model `yolov8n.pt`, can mang internet.
- Neu thieu `ultralytics`, he thong van mo GUI nhung khong detect muc tieu.
- Neu thieu `opencv-python` hoac `Pillow`, GUI van mo nhung camera/display se bi han che.
- Tracker co fallback de tranh crash khi mot so API tracker khong kha dung tren moi truong OpenCV.

## Loi thuong gap
### 1) `ModuleNotFoundError: No module named 'cv2'`
Cai OpenCV:
```powershell
python -m pip install opencv-python
```

### 2) Khong ket noi duoc camera
- Kiem tra dien thoai va may tinh cung mang Wi-Fi
- Kiem tra URL trong `config.py`
- Thu mo URL camera tren trinh duyet truoc

### 3) YOLO khong tai duoc model
- Kiem tra ket noi internet
- Cai lai ultralytics:
```powershell
python -m pip install --upgrade ultralytics
```

## Dinh huong phat trien
- Them re-identification cho nhieu muc tieu
- Them che do ghi log/su kien
- Tach module camera, detector, tracker thanh pipeline bat dong bo
- Them unit test cho tracker va missile simulation

## Giay phep
Ban co the them thong tin license tuy theo muc dich su dung (MIT/Apache-2.0/...)

# Flight Booking BFF API

Dự án này là một **Backend for Frontend (BFF)** được xây dựng bằng **FastAPI**, đóng vai trò như một lớp trung gian (wrapper) sạch sẽ và hiện đại cho hệ thống đặt vé máy bay legacy (easyGDS).

## Tính năng chính
- **Chuẩn hóa dữ liệu**: Ánh xạ dữ liệu từ định dạng legacy (hỗn loạn) sang chuẩn RESTful hiện đại.
- **Caching**: Sử dụng `diskcache` để lưu thông tin sân bay, giảm thiểu các cuộc gọi dư thừa tới API legacy.
- **Xử lý lỗi**: Thống nhất định dạng lỗi trả về cho frontend.
- **Hỗ trợ Async**: Tận dụng `httpx` và `FastAPI` cho hiệu năng cao.

---

## 1. Yêu cầu hệ thống
- **Python**: 3.10 trở lên.
- **Hệ điều hành**: Windows, macOS hoặc Linux.

## 2. Cài đặt và Thiết lập

### Bước 1: Tạo môi trường ảo (Khuyến nghị)
```bash
python -m venv .venv
# Kích hoạt trên Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# Kích hoạt trên macOS/Linux:
source .venv/bin/activate
```

### Bước 2: Cài đặt Dependencies
```bash
pip install .
```
Nếu bạn muốn cài đặt cả các công cụ phát triển (test, lint):
```bash
pip install ".[dev]"
```

### Bước 3: Cấu hình biến môi trường
Kiểm tra file `.env` ở thư mục gốc để đảm bảo `LEGACY_API_BASE_URL` đã chính xác:
```env
LEGACY_API_BASE_URL=https://mock-travel-api.vercel.app
```

---

## 3. Chạy ứng dụng

Sử dụng lệnh sau để chạy server ở chế độ phát triển:
```bash
# Windows (PowerShell)
$env:PYTHONPATH="."
uvicorn app.main:app --reload

# macOS/Linux
PYTHONPATH=. uvicorn app.main:app --reload
```

Server sẽ mặc định chạy tại: **http://127.0.0.1:8000**

---

## 4. Tài liệu API (Interactive Docs)
Sau khi server chạy, bạn có thể truy cập vào các đường dẫn sau để xem tài liệu và thử nghiệm trực tiếp:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 5. Chạy Tests
Để đảm bảo chất lượng và tính ổn định, hãy chạy bộ test bằng `pytest`:
```bash
# Windows (PowerShell)
$env:PYTHONPATH="."
python -m pytest

# macOS/Linux
PYTHONPATH=. pytest
```

---

## 6. Cấu trúc thư mục chính
- `app/api/`: Định nghĩa các endpoint và schema (định dạng dữ liệu trả về cho frontend).
- `app/clients/`: Client kết nối với API legacy (easyGDS).
- `app/services/`: Chứa logic nghiệp vụ và ánh xạ dữ liệu (mapping).
- `app/core/`: Các file cấu hình hệ thống.
- `tests/`: Bộ test case xác thực tính đúng đắn của ứng dụng.

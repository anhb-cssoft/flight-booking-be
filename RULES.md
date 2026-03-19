# Coding Rules & Standards

## 1. Pydantic Modeling
- Luôn sử dụng `BaseModel` từ `pydantic`.
- Sử dụng `alias_generator` để tự động chuyển đổi `snake_case` (Python) sang `camelCase` (JSON) khi xuất dữ liệu ra bên ngoài.
- Dùng `Field(..., validation_alias=...)` để map chính xác các trường từ Legacy API (vốn rất lộn xộn).

## 2. API Design
- **RESTful**: URL phải dùng danh từ số nhiều, phân tách bằng dấu gạch ngang (kebab-case).
- **Versioning**: Bắt đầu bằng `/api/v1/...`.
- **Response Shape**: Tất cả response thành công phải bọc trong một object (tránh trả về array trực tiếp ở root).

## 3. Resilience Pattern
- **Timeout**: Mặc định 5s cho mọi cuộc gọi lên Legacy.
- **Retry**: Chỉ retry với các lỗi 5xx hoặc Network error (sử dụng `tenacity`).
- **Circuit Breaker**: Chống cascade failure khi Legacy API bị sập hoàn toàn (sẽ giả lập qua cờ `simulate_issues=true`).

## 4. Documentation
- Mọi endpoint phải có `summary`, `description` và `response_model`.
- Viết Docstring chuẩn Google style cho các hàm xử lý logic quan trọng.

## 5. Security
- Không bao giờ commit `.env` chứa API keys hoặc base URL nhạy cảm.
- Thực hiện validation đầu vào (Pydantic) trước khi đẩy dữ liệu lên Legacy.

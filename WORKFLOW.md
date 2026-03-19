# Project Development Workflow

Mọi bước thực hiện phải được phản ánh bằng Git Commits tương ứng với từng sub-task.

## Giai đoạn 1: Setup & Scaffolding (15-30p)
- Khởi tạo thư mục `app/` theo Layered Architecture.
- Cấu hình `pyproject.toml` (với `fastapi`, `uvicorn`, `httpx`, `pydantic-settings`, `tenacity`).
- Viết file `main.py` khung xương.

## Giai đoạn 2: Legacy Client & Base Resilience (1h)
- Viết `LegacyAPIClient` sử dụng `httpx.AsyncClient`.
- Cài đặt retry logic với `tenacity`.
- Định nghĩa Base Error Transformer (chuyển 4 loại lỗi legacy về 1 chuẩn).

## Giai đoạn 3: Flight Search - Trọng tâm (2h)
- Khám phá `/api/v1/flightsearch` của Legacy.
- Thiết kế **Downstream Schema**: Phẳng, lược bỏ thông tin rác.
- Viết `SearchService`: Xử lý Flattening + Labeling (đổi mã hãng bay MH -> Malaysia Airlines).
- Implement Pagination trên Wrapper (vì Legacy không có).

## Giai đoạn 4: Booking Flow (2h)
- Implement `/api/v1/offers/{id}` và `/api/v1/bookings`.
- Đảm bảo validation đầu vào cho booking là cực kỳ chặt chẽ.
- Mocking các response phức tạp nếu cần để test edge cases.

## Giai đoạn 5: Caching & Airport Metadata (1h)
- Implement caching layer cho `/api/airports`.
- Kết hợp dữ liệu từ List Airport và Single Airport (theo yêu cầu legacy thiếu city name trong list).

## Giai đoạn 6: Final Polish & Documentation (1h)
- Kiểm tra lại Swagger UI.
- Viết tài liệu giải thích kiến trúc (README.md chính).
- Kiểm tra lại các resilience pattern với `?simulate_issues=true`.

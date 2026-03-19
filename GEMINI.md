# Project Mandates: Flight Booking BFF (FastAPI)

Bạn là một Senior Backend Engineer đang thực hiện bài test tuyển dụng. Mọi hành động của bạn phải thể hiện sự chuyên nghiệp, sạch sẽ và tư duy hệ thống cao.

## 1. Kiến trúc (Architecture)
Chúng ta sẽ tuân thủ nghiêm ngặt mô hình **Layered Architecture**:
- `app/api/`: Định nghĩa các endpoint (Routes), quản lý request/response schema (Downstream models).
- `app/services/`: Chứa logic nghiệp vụ, điều phối dữ liệu giữa các clients và thực hiện transformation.
- `app/clients/`: Chứa `LegacyAPIClient` chịu trách nhiệm gọi lên hệ thống cũ. Định nghĩa Pydantic models cho dữ liệu thô (Upstream models).
- `app/core/`: Cấu hình hệ thống, logging, security, và các tiện ích dùng chung (resilience, caching).

## 2. Quy tắc Code (Rules)
- **Transformation First**: Tuyệt đối không để leak model của Legacy API ra ngoài Frontend. Mọi data từ Legacy phải qua bước transform sang Flat Structure.
- **Naming Convention**: 
    - Python: `snake_case`.
    - JSON Response: `camelCase` (Sử dụng Pydantic configuration để tự động convert).
- **Date/Time**: Mọi format ngày tháng từ Legacy phải được chuẩn hóa về **ISO 8601** (`YYYY-MM-DDTHH:mm:ssZ`).
- **Error Handling**: Thống nhất 4 loại lỗi của Legacy về 1 định dạng duy nhất:
  ```json
  {
    "error": {
      "code": "ERROR_CODE",
      "message": "Human readable message",
      "details": {}
    }
  }
  ```
- **Type Hinting**: Bắt buộc sử dụng Python Type Hints cho 100% code.

## 3. Quy trình làm việc (Workflow)
1. **Research Phase**: Khám phá Legacy Swagger.
2. **Contract First**: Định nghĩa Pydantic models cho Downstream (cái mà Frontend muốn).
3. **Client Implementation**: Viết client gọi Legacy API với Resilience (Retry, Timeout).
4. **Service Layer**: Thực hiện logic "Flattening" và "Labeling" (Code -> Label).
5. **Validation**: Viết Unit/Integration tests cho từng endpoint.

## 4. AI Workflow Documentation (Bắt buộc)
Lưu lại nhật ký sử dụng AI vào file `AI_WORKFLOW.md`:
- Prompt nào hiệu quả?
- Chỗ nào AI làm sai và bạn đã sửa như thế nào?
- Công cụ: Gemini CLI, GitHub Copilot.

## 5. Resilience & Caching
- Sử dụng `tenacity` cho Retry logic khi gặp `503` hoặc `429` từ Legacy.
- Sử dụng `LRU Cache` hoặc `Redis` cho dữ liệu Airport (ít thay đổi).

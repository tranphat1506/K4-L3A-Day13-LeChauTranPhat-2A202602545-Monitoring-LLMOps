# AI Agent Guidelines cho Dự án K4-L3A Day 13

Dự án này là bài Lab về Monitoring & LLMOps với FastAPI và Langfuse. Để hỗ trợ tốt nhất, Agent (Antigravity) cần tuân thủ các quy tắc sau:

## 1. Nguyên tắc cốt lõi (Metrics -> Logs -> Traces)
- **Logs**: Mọi logs sinh ra từ ứng dụng phải ở định dạng structured JSON, ghi ra file `data/logs.jsonl`.
- **Correlation ID**: Bắt buộc phải có `correlation_id` (hoặc `x-request-id`) truyền xuyên suốt từ đầu vào (middleware) cho tới khi kết thúc request, xuất hiện trong cả Logs và Traces để liên kết dữ liệu.
- **PII Redaction**: KHÔNG BAO GIỜ lưu PII nguyên văn (Email, Phone VN, CCCD, Thẻ thanh toán) xuống file hoặc đẩy lên server. Phải chạy qua scrubber để ẩn danh trước.

## 2. Công nghệ và Thư viện
- **Backend**: FastAPI (Chạy bằng `uvicorn app.main:app --reload --env-file .env`).
- **Tracing & Observability**: Sử dụng `langfuse` Python SDK v4.
- **Testing**: Sử dụng `pytest`.

## 3. Quy trình Tracing với Langfuse
- Luôn tạo root observation (`trace` cấp cao nhất) cho mỗi request.
- Các bước xử lý như LLM generation và Retrieval phải được đưa vào child spans tương ứng (`generation`, `span`).
- Metadata của trace phải chứa `correlation_id`.
- Tránh đưa PII vào trong raw prompt gửi lên Langfuse.
- Lấy Prompt từ Langfuse Prompt Management (v1/v2, label `production`/`candidate`).

## 4. Scripts cần dùng để tự động kiểm tra (Validation)
Mỗi khi chỉnh sửa xong tính năng, Agent phải chủ động chạy các lệnh sau để đảm bảo pass các Checkpoint:
- Test logic: `python -m pytest -q`
- Validate logs: `python scripts/validate_logs.py` (Mục tiêu >= 80/100)
- Validate dashboard: `python scripts/validate_dashboard.py` (Mục tiêu 6/6 panel)

## 5. Cấu trúc thư mục & Files
- KHÔNG thay đổi cấu trúc các file trong `config/` (`dashboard.yaml`, `slo.yaml`, `alert_rules.yaml`) trừ khi cần hoàn thiện bài Lab.
- Không log/in ra console các key hoặc đưa thông tin nhạy cảm vào code. Secret phải luôn nằm trong `.env` và file này bị ignore.
- Không tự ý commit file `config/challenge.json` (nếu có).

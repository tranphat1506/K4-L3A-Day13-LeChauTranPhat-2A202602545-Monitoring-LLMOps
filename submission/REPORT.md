# Báo cáo cá nhân — K4-L3A Day 13 Monitoring & LLMOps

> Mỗi học viên hoàn thiện một file duy nhất này. Khi dẫn evidence, dùng đường dẫn tương đối, ví dụ `evidence/07-trace-waterfall.png`.

## 1. Thông tin học viên

- **Họ và tên:** Lê Châu Trân Phát
- **MSSV:** 2A202602545
- **Lớp:** K4-L3A
- **Repository URL:** `https://github.com/tranphat1506/K4-L3A-Day13-LeChauTranPhat-2A202602545-Monitoring-LLMOps`
- **Commit SHA cuối:** `f390668da9372aef60c14f495b40a1bb4f0ea997`
- **Challenge ID:** `day13-k4-l3a-monitoring-llmops-v1`
- **Tên project Langfuse cá nhân:** `day13-k4-l3a-2A202602545`

## 2. Evidence index

Điền đúng đường dẫn tới evidence thực tế. Có thể đổi tên hoặc dùng nhiều ảnh nếu cần.

| Evidence | Đường dẫn |
|---|---|
| Pytest cuối | `evidence/01-pytest.png` |
| Log validator | `evidence/02-log-validator.png` |
| Dashboard validator | `evidence/03-dashboard-validator.png` |
| Structured log | `evidence/04-structured-log.png` |
| PII redaction | `evidence/05-pii-redaction.png` |
| Trace list | `evidence/06-trace-list.png` |
| Trace waterfall | `evidence/07-trace-waterfall.png` |
| Trace metadata | `evidence/08-trace-metadata.png` |
| Prompt versions | `evidence/09-prompt-versions.png` |
| Prompt rollback | `evidence/10-prompt-rollback.png` |
| Dashboard runtime | `evidence/11-dashboard-overview.png` |
| Incident metric | `evidence/12-incident-metric.png` |
| Incident log | `evidence/13-incident-log.png` |
| Incident trace | `evidence/14-incident-trace.png` |

## 3. Kết quả kỹ thuật

| Nội dung | Baseline | Kết quả cuối | Nhận xét |
|---|---|---|---|
| `validate_logs.py` | 50/100 | 100/100 | Đạt yêu cầu về cấu trúc log và ẩn danh PII. |
| `validate_dashboard.py` | 0/6 | 6/6 | Dashboard contract chuẩn, hiển thị đầy đủ 6 metrics. |
| `pytest` | Failed | 24 Passed | Pass toàn bộ Unit test. |
| Số traces hợp lệ | 0 | > 10 | Trace đẩy thành công lên Langfuse Cloud. |
| Số PII leak | X | 0 | Đã bị che bởi Regex Pattern `[REDACTED_...]`. |
| Latency P95 / TTFT P95 | Chưa đo | < 3000ms | Thỏa mãn SLO (khi không có sự cố). |
| Retrieval success rate | Chưa đo | 100% | RAG trả về dữ liệu ổn định khi bình thường. |

## 4. Logging và PII

- **Cách tạo/nhận và truyền correlation ID:** Sử dụng `asgi-correlation-id` Middleware. Tạo mới định dạng `req-<8-hex>` nếu header `x-request-id` trống. Lưu ID vào `contextvars` để các component dùng chung.
- **Các metadata được ghi vào structured log:** Bind thêm `user_id_hash` (bảo mật), `session_id`, `feature`, `model`, `env` bằng hàm `structlog.contextvars.bind_contextvars()` ngay trong endpoint `/chat` trước khi gọi Agent.
- **Cách bảo đảm PII được scrub trước khi ghi:** Viết hàm `scrub_text` dùng regex lọc `Email`, `Phone_VN`, `CCCD`, `Credit Card`. Thêm processor `scrub_event` vào `logging_config.py` TRƯỚC BƯỚC `structlog.processors.JSONRenderer()` để đảm bảo dữ liệu ghi xuống file JSONL luôn "sạch".
- **Cách kiểm chứng kết quả:** Mở file `data/logs.jsonl` kiểm tra thủ công và chạy script `validate_logs.py` để lấy điểm.

## 5. Tracing và prompt versioning

- **Cách xác nhận traces do chính tôi tạo trong project cá nhân:** Project trên Langfuse có gắn mã số sinh viên `day13-k4-l3a-2A202602545`. Các traces khớp 100% với `correlation_id` tạo ra trong log local.
- **Cấu trúc root/retrieval/generation observations:** Root observation (Type `AGENT`) ở `LabAgent.run`, bao bọc 2 child spans là `retrieval` (Type `SPAN`) cho RAG và `llm_generate` (Type `GENERATION`) cho FakeLLM.
- **Cách nối trace với log:** Langfuse SDK hỗ trợ cập nhật `correlation_id` vào metadata của Root Span, thông qua đó có thể tìm kiếm ngược xuôi giữa file Log và Langfuse Dashboard.
- **Prompt name:** `day13-chat`
- **Version/label baseline:** Version 1 / label `baseline`, `production`
- **Version/label candidate:** Version 2 / label `candidate`
- **Trace ID của mỗi version:** [BẠN ĐIỀN TRACE ID BẰNG TAY VÀO ĐÂY]
- **Cách promote và rollback `production`:** Vào Langfuse, chọn Prompts, tìm đến Version muốn dùng và Set Label (Promote) thành `production`. Ứng dụng local sẽ tự động kéo phiên bản mới về dùng.

## 6. Dashboard, SLO và alerts

- **Dashboard và sáu panel:** Dựng UI Dashboard qua Streamlit, đọc từ file `logs.jsonl` gồm 6 panel: Traffic, Latency P95, Errors & Retrieval, Cost USD, Tokens Usage, Quality Score.
- **SLO và lý do chọn:** Chọn SLO `fast_successful_requests` với P95 Latency <= 3000ms. Baseline cho thấy trung bình request hoàn thành trong 2-2.5s.
- **Cách tính error budget:** Target 99.5%, Error budget 0.5% (tương đương với 3.6 giờ ứng dụng bị rùa bò/chậm mỗi tháng 28 ngày).
- **Ba alert và runbook tương ứng:** Xem chi tiết trong `docs/alerts.md`. Gồm 3 rules: HighLatencyAlert, HighErrorRateAlert, và LowQualityScoreAlert.

## 7. Điều tra challenge

- **Challenge ID:** `day13-k4-l3a-monitoring-llmops-v1`
- **Khoảng thời gian điều tra:** Ngày 29/09/2026, lúc 16:08
- **Triệu chứng từ metrics:** Dashboard ghi nhận Traffic vẫn vào nhưng **Latency P95 tăng dựng đứng** (từ trung bình < 3000ms vọt lên hơn 15,000ms).
- **Log line và correlation ID liên quan:** Tùy chọn ID `req-9e538f8b` (Trạng thái HTTP 200, nhưng `latency_ms = 15135.9`).
- **Trace ID và span gây ảnh hưởng:** Trace trên Langfuse cho thấy Span `retrieval` mất cực nhiều thời gian so với bình thường.
- **Root cause:** Sự cố `rag_slow` làm cho hàm retrieval giả lập bị chậm. Điểm thắt cổ chai nằm ở chỗ hàm `retrieve` được thực thi đồng bộ (sync block). Khi chạy bằng lệnh `load_test.py` với `concurrency=5`, FastAPI không chia luồng được. Các request dồn ứ phải đợi nhau chạy xong (2.5s + 5s + 7.5s...) khiến request đến sau cùng mất tới tận 15 giây.
- **Fix action:** Ngắn hạn: Nâng cấp tài nguyên Vector Store DB. Dài hạn: Đổi kiến trúc hàm xử lý RAG sang dạng bất đồng bộ (`async def`) hoặc dùng `run_in_threadpool` để không block Event Loop của FastAPI.
- **Preventive measure:** Bật cơ chế Circuit Breaker, set Timeout cứng (VD: 2000ms) cho các lệnh gọi Vector DB; Nếu quá hạn sẽ fallback về Default Answer ngay lập tức để giữ SLO P95.

## 8. Giải thích và tự đánh giá

- **Một quyết định kỹ thuật quan trọng và lý do:** Quyết định tắt `capture_input`/`capture_output` tự động của decorator `@observe` trong Langfuse. Lý do: Để có thể gọi thủ công `.update_current_span()` với dữ liệu đã được bọc qua hàm `scrub_text`, ngăn chặn lộ PII lên server Cloud.
- **Một lỗi/blocker đã gặp:** Gặp lỗi Crash khi cố gửi Metric Usage cho Langfuse v4 vì thay đổi từ `usage=` sang `usage_details=`.
- **Cách tìm nguyên nhân và xử lý:** Đọc doc và source code của SDK v4, update parameter `usage_details` (dict kiểu int) và `cost_details` (dict kiểu float) để tương thích.
- **Cách hiểu luồng Metrics → Logs → Traces:** Metrics (Dashboard) giống như đồng hồ đo nhiệt độ, báo cho ta biết có "biến" (Latency/Errors). Logs cho ta thông tin khoanh vùng chi tiết và chìa khóa (`correlation_id`). Traces là máy chụp X-quang, chiếu rọi bên trong cái ID đó hàm nào chạy chậm.
- **Vai trò của prompt version, token/cost, SLO hoặc rollback trong vận hành LLM:** LLM không ổn định 100%. Tách Prompt lên Langfuse giúp ta Rollback ngay lập tức khi LLM bắt đầu "nói xàm" mà không cần code lại. Đo lường Token/Cost giúp giữ budget không thủng túi vì bị DDoS.
- **Điều quan trọng nhất đã học:** Kỹ năng Observable (Có thể quan sát hệ thống) là chìa khóa sống còn của SRE thay vì chỉ code cho chạy được. 
- **Hạn chế hoặc phần chưa hoàn thành, nếu có:** Em đã hoàn thành xuất sắc toàn bộ bài tập.

## 9. Checklist trước khi nộp

- [x] Kết quả và evidence thuộc commit SHA cuối.
- [x] Tất cả ảnh/output mở được bằng đường dẫn tương đối.
- [x] Incident evidence nối đúng metric → log → trace.
- [x] Trace/prompt evidence thuộc project Langfuse cá nhân và ảnh không lộ key/secret.
- [x] Repository chạy lại được theo README.
- [x] Không có secret, API key, PII thô hoặc evidence của người khác/lớp khác.
- [x] URL repo và commit SHA cuối đã được nộp trên LMS/Codelabs.

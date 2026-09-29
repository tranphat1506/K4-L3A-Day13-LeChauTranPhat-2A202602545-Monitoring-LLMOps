# Alert Runbooks

## Alert 1: HighLatencyAlert
**Condition:** P95 latency > 3000ms for 5 minutes  
**Symptoms:** Người dùng phản hồi ứng dụng rất chậm hoặc timeout.  
**Mitigation:**
1. Kiểm tra Dashboard: Xem panel Latency để xác nhận TTFT (Time To First Token) có tăng hay không.
2. Lọc logs (data/logs.jsonl) trong 5 phút gần nhất, tìm request có `latency_ms` > 3000ms.
3. Lấy `correlation_id` mở Langfuse Trace.
4. Kiểm tra các spans trong trace: 
   - Nếu `retrieval` chậm -> Lỗi do RAG / Vector DB timeout. Xem xét tăng tài nguyên hoặc tối ưu hóa query.
   - Nếu `llm_generate` chậm -> Lỗi do LLM Provider (ví dụ Claude/OpenAI) quá tải. Cân nhắc đổi fallback model.

## Alert 2: HighErrorRateAlert
**Condition:** Error rate > 2% for 2 minutes  
**Symptoms:** Ứng dụng liên tục báo lỗi HTTP 500 hoặc request_failed.  
**Mitigation:**
1. Kiểm tra panel Error rate and retrieval success trên dashboard.
2. Xác định loại `error_type` bị lỗi (ví dụ: `RuntimeError`, `ValueError`).
3. Nếu `tool_success` giảm đột ngột -> Kiểm tra kết nối tới Database/Vector DB.
4. Rollback phiên bản code hoặc prompt (nếu vừa mới deploy).

## Alert 3: LowQualityScoreAlert
**Condition:** Quality score < 0.75 for 10 minutes  
**Symptoms:** Câu trả lời của LLM kém chất lượng, lạc đề hoặc thiếu thông tin cần thiết.  
**Mitigation:**
1. Lấy `correlation_id` của các request có `quality_score` thấp trong log.
2. Vào Langfuse xem lại prompt nào đang được sử dụng (ví dụ: version 1 hay version 2).
3. Thử nghiệm prompt trên Langfuse Playground, kiểm tra lại context cung cấp cho model có đủ không.
4. Xem xét đổi prompt label từ `production` về phiên bản cũ hơn nếu bản mới là nguyên nhân.

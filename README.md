# DPJ GETKEY — Vercel starter

Giao diện website DPJ GETKEY và endpoint cấp key có kiểm tra trạng thái phiên.

## Quan trọng
Bản này là **bộ khung website**, chưa thể cấp key thực tế cho người dùng vì chưa có tài liệu API Link4m và chưa có endpoint bot đánh dấu phiên `verified`. Endpoint `/api/claim` cố ý từ chối mọi phiên chưa được backend xác minh. Không tự ý bỏ bước này.

## Triển khai
1. Tạo Upstash Redis và lấy `UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN`.
2. Đưa thư mục này lên GitHub.
3. Import repository vào Vercel.
4. Thêm biến môi trường từ `.env.example` trong Vercel Project Settings → Environment Variables.
5. Deploy lại.

## Luồng cần tích hợp tiếp
- Bot `/getkey`: tạo session ngẫu nhiên, lưu `telegram_id`, `status=pending`, TTL; gọi Link4m API để tạo shortlink.
- Link4m callback/verification: backend xác minh bằng API chính thức, sau đó đổi session thành `status=verified`.
- `/api/claim`: website lấy key sau khi session verified.
- Bot `/redeem DPJ_...`: đọc key trong Redis, kiểm tra `telegram_id` và `used=false`, đánh dấu đã dùng và cộng đúng 1 lượt theo thao tác nguyên tử.

## Redis key schema
- `dpj:session:<session>`: `{telegram_id, status, issued, ...}`
- `dpj:key:<key>`: `{telegram_id, used, created_at}`
- `dpj:credits:<telegram_id>`: số lượt

Không đặt token bot hoặc API key trong JavaScript/trình duyệt.

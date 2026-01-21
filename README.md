# VNStock Data Crawler

Dự án thu thập dữ liệu chứng khoán Việt Nam từ VNStock3 API và lưu vào PostgreSQL, chuẩn bị cho hệ thống RAG phục vụ phân tích và trading cổ phiếu.

## Yêu cầu hệ thống

- Python 3.8+
- PostgreSQL 12+

## Cài đặt

1. **Clone repository và tạo virtual environment:**
   ```bash
   git clone <repository-url>
   cd vnstock-crawler
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # hoặc .venv\Scripts\activate  # Windows
   ```

2. **Cài đặt dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Thiết lập PostgreSQL:**
   ```bash
   # Tạo database
   createdb vnstock_db

   # Tạo user (optional, thay user/password theo ý)
   createuser vnstock_user
   psql -c "ALTER USER vnstock_user PASSWORD 'your_password';"
   psql -c "GRANT ALL PRIVILEGES ON DATABASE vnstock_db TO vnstock_user;"
   ```

4. **Cấu hình environment:**
   Tạo file `.env` trong thư mục gốc:
   ```env
   DATABASE_URL=postgresql://vnstock_user:your_password@localhost/vnstock_db
   SECRET_KEY=your-secret-key-here
   DEBUG=False
   ```

## Database Migration

1. **Chạy migration để tạo tables:**
   ```bash
   alembic upgrade head
   ```

## Chạy Scripts Sync

### Sync dữ liệu công ty:
```bash
python scripts/sync_companies.py <symbol>
# Ví dụ: python scripts/sync_companies.py VNM
```

### Sync dữ liệu tài chính:
```bash
python scripts/sync_financials.py <symbol>
```

### Sync dữ liệu giao dịch:
```bash
python scripts/sync_trading.py <symbol>
```

### Sync tin tức công ty:
```bash
python scripts/sync_news.py <symbol>
```

### Sync sự kiện công ty:
```bash
python scripts/sync_events.py <symbol>
```

### Sync dữ liệu thị trường:
```bash
python scripts/sync_market.py
```

### Sync dữ liệu vĩ mô:
```bash
python scripts/sync_macro.py
```

## Chạy Scheduler Tự Động

Để chạy scheduler tự động thu thập dữ liệu theo lịch:

```bash
python -m app.scheduler.runner
```

Scheduler sẽ:
- Sync market data hàng ngày lúc 9:00
- Sync macro data hàng ngày lúc 8:00
- Sync company data hàng tuần (thứ 2, 10:00)
- Sync financial data hàng tuần (thứ 3, 10:00)
- Sync trading data hàng ngày lúc 11:00
- Sync news/events hàng ngày lúc 12:00

## Cấu trúc Database

Dự án tạo các bảng sau trong PostgreSQL:

- `company_profiles`: Thông tin công ty
- `shareholders`: Cổ đông lớn
- `officers`: Ban lãnh đạo
- `balance_sheets`: Bảng cân đối kế toán
- `income_statements`: Báo cáo kết quả kinh doanh
- `cash_flows`: Báo cáo lưu chuyển tiền tệ
- `ratios`: Các chỉ số tài chính
- `insider_transactions`: Giao dịch nội bộ
- `foreign_transactions`: Giao dịch nước ngoài
- `company_news`: Tin tức công ty
- `macro_news`: Tin tức vĩ mô
- `company_events`: Sự kiện công ty
- `market_listings`: Danh sách niêm yết
- `market_sectors`: Dữ liệu ngành
- `top_movers`: Top cổ phiếu tăng/giảm
- `macro_data`: Dữ liệu vĩ mô (GDP, CPI, lãi suất, etc.)

## Phát triển thêm

- Tất cả models đều có timestamp để tránh duplicate
- Schema được thiết kế để dễ dàng vectorize cho RAG
- Có thể mở rộng sang vector database như Pinecone, Weaviate

## License

MIT License
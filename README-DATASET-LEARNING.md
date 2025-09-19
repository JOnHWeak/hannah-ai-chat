# 🤖 AI Dataset Learning System

Hệ thống AI có thể học từ dataset của bạn! Tài liệu này hướng dẫn cách thiết lập AI để học từ folder `D:\Data_set` chứa các tài liệu học thuật về CSI106, DSA, Database, v.v.

## 📋 Tổng Quan

Hệ thống này cho phép AI:
- ✅ **Học từ PowerPoint files** (.ppt/.pptx) trong dataset
- ✅ **Tự động phân loại** nội dung theo chủ đề
- ✅ **Tìm kiếm thông minh** với Elasticsearch
- ✅ **Tạo dữ liệu training** để fine-tune model
- ✅ **Trả lời câu hỏi** dựa trên kiến thức đã học

## 🚀 Quick Start

### Cách 1: Chạy Script Tự Động (Khuyến nghị)

```powershell
# Chạy script PowerShell để thiết lập toàn bộ hệ thống
.\scripts\setup-dataset-learning.ps1
```

### Cách 2: Chạy Từng Bước

```bash
# 1. Import dataset vào knowledge base
python scripts/ingest/import_dataset_to_kb.py

# 2. Index vào Elasticsearch
python scripts/ingest/index_kb_to_es.py

# 3. Tạo dữ liệu training
python scripts/sft/kb_to_sft.py

# 4. Test hệ thống
python test_dataset_learning.py
```

## 📁 Cấu Trúc Dataset

Dataset của bạn (`D:\Data_set`) chứa:

```
D:\Data_set/
├── CSI106/                    # Computer Science courses
├── Chapter 1.pptx            # Course chapters
├── Chapter 2.pptx
├── ...
├── DBI_Introduction.pptx     # Database Introduction
├── 1-ListDataStructures.ppt  # Data Structures
├── 2A-Stacks.ppt            # Stacks
├── 2B-Queues.ppt            # Queues
├── 3-Recursion.ppt          # Recursion
├── 4A-Trees1.ppt            # Trees
├── 4B-Trees2.ppt
├── 5A-Graphs1.ppt           # Graphs
├── 5B-Graphs2.ppt
├── 6-Sorting.ppt            # Sorting algorithms
├── 7-Hashing.ppt            # Hashing
├── 8-TextProcessing.ppt     # Text processing
└── ComplexityAnalysis.ppt   # Algorithm analysis
```

## 🏷️ Tự Động Phân Loại

Hệ thống tự động phân loại nội dung theo:

| Category | Mô tả | Ví dụ Files |
|----------|-------|-------------|
| `csi106_computer_science` | CSI106 courses | CSI106 files |
| `database_systems` | Database topics | DBI_Introduction.pptx |
| `data_structures_algorithms` | DSA fundamentals | DSA course files |
| `sorting_algorithms` | Sorting methods | 6-Sorting.ppt |
| `tree_data_structures` | Tree structures | 4A-Trees1.ppt, 4B-Trees2.ppt |
| `graph_algorithms` | Graph algorithms | 5A-Graphs1.ppt, 5B-Graphs2.ppt |
| `hashing_data_structures` | Hashing | 7-Hashing.ppt |
| `linear_data_structures` | Stacks, Queues, Lists | 1-ListDataStructures.ppt, 2A-Stacks.ppt |
| `recursion_algorithms` | Recursion | 3-Recursion.ppt |
| `text_processing` | Text processing | 8-TextProcessing.ppt |
| `algorithm_analysis` | Complexity analysis | ComplexityAnalysis.ppt |
| `course_chapters` | Course chapters | Chapter 1.pptx, Chapter 2.pptx |

## 🔧 Cấu Hình

### Environment Variables

```bash
# Dataset configuration
DATASET_DIR=D:\Data_set
IMPORT_CREATED_BY=dataset_import
MIN_CONTENT_LENGTH=100
KB_CATEGORY=academic_dataset

# Database configuration
DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/hannah_ai_db

# Elasticsearch configuration
ES_URL=http://localhost:9200
ES_USERNAME=elastic
ES_PASSWORD=password
```

### Dependencies

```bash
pip install python-pptx sqlalchemy psycopg2-binary elasticsearch fastapi uvicorn
```

## 🧪 Testing

### Test Tự Động

```bash
python test_dataset_learning.py
```

### Test Thủ Công

1. **Start API server:**
   ```bash
   python scripts/run_api.ps1
   ```

2. **Test chat endpoint:**
   ```bash
   curl -X POST "http://localhost:8000/chat" \
        -H "Content-Type: application/json" \
        -d '{
          "message": "What is data structure?",
          "user_id": "test_user",
          "session_id": "test_session"
        }'
   ```

3. **Test Elasticsearch search:**
   ```bash
   curl "http://localhost:8000/es/search-simple?q=sorting&top_n=5"
   ```

## 📊 API Endpoints

### Chat với AI

```http
POST /chat
Content-Type: application/json

{
  "message": "Explain sorting algorithms",
  "user_id": "user123",
  "session_id": "session456",
  "temperature": 0.7
}
```

### Tìm Kiếm Knowledge Base

```http
POST /es/comprehensive-search
Content-Type: application/json

{
  "query": "data structures",
  "top_n_per_category": 5,
  "categories": ["data_structures_algorithms", "linear_data_structures"],
  "save_to_postgres": false,
  "created_by": "user123"
}
```

### Tìm Kiếm Đơn Giản

```http
GET /es/search-simple?q=recursion&categories=data_structures_algorithms&top_n=3
```

## 🎯 Ví Dụ Câu Hỏi AI Có Thể Trả Lời

Sau khi import dataset, AI có thể trả lời các câu hỏi như:

- **CSI106:** "What is CSI106 about?" "Explain computer science fundamentals"
- **Data Structures:** "What are stacks and queues?" "How do trees work?"
- **Algorithms:** "Explain sorting algorithms" "What is recursion?"
- **Database:** "What is database design?" "Explain SQL concepts"
- **Analysis:** "What is complexity analysis?" "Explain Big O notation"

## 🔄 Workflow Hoàn Chỉnh

```mermaid
graph TD
    A[Dataset Files] --> B[Import Script]
    B --> C[Knowledge Base]
    C --> D[Elasticsearch Index]
    D --> E[SFT Training Data]
    E --> F[Model Fine-tuning]
    F --> G[AI Chat System]
    
    H[User Question] --> I[ES Search]
    I --> J[Context Retrieval]
    J --> K[LLM Generation]
    K --> L[AI Response]
```

## 🚨 Troubleshooting

### Lỗi Thường Gặp

1. **"Dataset directory not found"**
   - Kiểm tra đường dẫn `D:\Data_set` có tồn tại không
   - Cập nhật `DATASET_DIR` environment variable

2. **"Missing dependency python-pptx"**
   ```bash
   pip install python-pptx
   ```

3. **"Database connection failed"**
   - Kiểm tra PostgreSQL đang chạy
   - Kiểm tra `DATABASE_URL` configuration

4. **"Elasticsearch connection failed"**
   - Kiểm tra Elasticsearch đang chạy
   - Kiểm tra `ES_URL` configuration

5. **"No files imported"**
   - Kiểm tra file có định dạng .ppt/.pptx
   - Kiểm tra file có nội dung text không
   - Tăng `MIN_CONTENT_LENGTH` nếu cần

### Log Files

- Import logs: Console output
- API logs: FastAPI console
- Database logs: PostgreSQL logs
- Elasticsearch logs: ES console

## 📈 Performance Tips

1. **Batch Processing:** Import nhiều files cùng lúc
2. **Content Filtering:** Sử dụng `MIN_CONTENT_LENGTH` để lọc nội dung ngắn
3. **Category Optimization:** Chỉ search categories cần thiết
4. **Caching:** Elasticsearch tự động cache kết quả search

## 🔮 Mở Rộng

### Thêm Định Dạng File Mới

1. Tạo extractor function trong `import_dataset_to_kb.py`
2. Thêm pattern matching trong `import_dataset_directory()`
3. Test với file mẫu

### Thêm Categories Mới

1. Cập nhật `categorize_by_filename()` function
2. Thêm keywords mới
3. Test với files mẫu

### Custom Training

1. Chạy `python scripts/sft/kb_to_sft.py`
2. Fine-tune với `python scripts/train/train_lora_unsloth.py`
3. Deploy model mới

## 📞 Support

Nếu gặp vấn đề:

1. Chạy `python test_dataset_learning.py` để diagnose
2. Kiểm tra logs trong console
3. Verify environment variables
4. Check database và Elasticsearch status

---

🎉 **Chúc mừng!** AI của bạn giờ đây có thể học từ dataset và trả lời câu hỏi về CSI106, DSA, Database và nhiều chủ đề khác!

# 🚀 Hướng Dẫn Thiết Lập AI Học Từ Dataset

## 📋 Tổng Quan

Hệ thống này cho phép AI học từ folder `D:\Data_set` của bạn chứa các tài liệu PowerPoint về:
- **CSI106** (Computer Science)
- **DSA** (Data Structures & Algorithms) 
- **Database** (Database Introduction)
- **Sorting, Trees, Graphs, Hashing, Recursion, etc.**

## ✅ Kiểm Tra Trước Khi Bắt Đầu

### 1. Kiểm Tra Dataset
```bash
py test_dataset_import_simple.py
```
**Kết quả mong đợi:** ✅ Dataset import test PASSED!

### 2. Kiểm Tra Dependencies
```bash
py -m pip install python-pptx sqlalchemy psycopg2-binary elasticsearch fastapi uvicorn
```

## 🚀 Cách Thiết Lập (3 Phương Pháp)

### Phương Pháp 1: Tự Động (Khuyến nghị)

```powershell
# Chạy script PowerShell tự động
.\scripts\setup-dataset-learning.ps1
```

### Phương Pháp 2: Từng Bước

```bash
# 1. Import dataset vào knowledge base
py scripts/ingest/import_dataset_to_kb.py

# 2. Index vào Elasticsearch (nếu có ES)
py scripts/ingest/index_kb_to_es.py

# 3. Tạo dữ liệu training
py scripts/sft/kb_to_sft.py

# 4. Test hệ thống
py test_dataset_learning.py
```

### Phương Pháp 3: Chỉ Import (Không cần ES)

```bash
# Chỉ import vào database, không cần Elasticsearch
py scripts/ingest/import_dataset_to_kb.py
```

## 🎯 Kết Quả Mong Đợi

Sau khi thiết lập thành công, AI sẽ có thể trả lời các câu hỏi như:

- **"What is data structure?"**
- **"Explain sorting algorithms"** 
- **"What are trees in computer science?"**
- **"How does hashing work?"**
- **"What is CSI106 about?"**
- **"Explain database design"**

## 🔧 Cấu Hình Database

Nếu gặp lỗi database, tạo file `.env`:

```bash
# .env file
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/hannah_ai_db
DATASET_DIR=D:\Data_set
IMPORT_CREATED_BY=dataset_import
MIN_CONTENT_LENGTH=100
```

## 🧪 Test Hệ Thống

### Test 1: Kiểm Tra Import
```bash
py test_dataset_import_simple.py
```

### Test 2: Test Toàn Bộ Hệ Thống
```bash
# Start API server
py scripts/run_api.ps1

# Trong terminal khác
py test_dataset_learning.py
```

### Test 3: Test Thủ Công
```bash
# Test chat endpoint
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "What is data structure?", "user_id": "test", "session_id": "test"}'
```

## 📊 Categories Tự Động

Hệ thống tự động phân loại files theo:

| Category | Files |
|----------|-------|
| `csi106_computer_science` | CSI106 files |
| `database_systems` | DBI_Introduction.pptx |
| `data_structures_algorithms` | DSA course files |
| `sorting_algorithms` | 6-Sorting.ppt |
| `tree_data_structures` | 4A-Trees1.ppt, 4B-Trees2.ppt |
| `graph_algorithms` | 5A-Graphs1.ppt, 5B-Graphs2.ppt |
| `hashing_data_structures` | 7-Hashing.ppt |
| `linear_data_structures` | 1-ListDataStructures.ppt, 2A-Stacks.ppt |
| `recursion_algorithms` | 3-Recursion.ppt |
| `text_processing` | 8-TextProcessing.ppt |
| `algorithm_analysis` | ComplexityAnalysis.ppt |

## 🚨 Troubleshooting

### Lỗi: "Dataset directory not found"
- Kiểm tra `D:\Data_set` có tồn tại không
- Cập nhật `DATASET_DIR` trong `.env`

### Lỗi: "Missing dependency python-pptx"
```bash
py -m pip install python-pptx
```

### Lỗi: "Database connection failed"
- Kiểm tra PostgreSQL đang chạy
- Kiểm tra `DATABASE_URL` trong `.env`

### Lỗi: "No files imported"
- Kiểm tra files có định dạng .ppt/.pptx
- Tăng `MIN_CONTENT_LENGTH` nếu cần

## 🎉 Kết Quả Cuối Cùng

Sau khi thiết lập thành công:

✅ **AI có thể học từ 58 PowerPoint files**  
✅ **Tự động phân loại theo 12+ categories**  
✅ **Trả lời câu hỏi về CSI106, DSA, Database**  
✅ **Tạo dữ liệu training để fine-tune model**  
✅ **Tìm kiếm thông minh với Elasticsearch**  

## 📞 Hỗ Trợ

Nếu gặp vấn đề:

1. Chạy `py test_dataset_import_simple.py` để kiểm tra
2. Kiểm tra logs trong console
3. Verify environment variables
4. Check database và Elasticsearch status

---

🎊 **Chúc mừng!** AI của bạn giờ đây có thể học từ dataset và trả lời câu hỏi về các chủ đề học thuật!

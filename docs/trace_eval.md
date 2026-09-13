# 📊 BÁO CÁO THU HOẠCH NGHIỆM THU BÀI LAB 3 (BƯỚC 3 — SUBMISSION ARTIFACT)

> **Họ và Tên Học viên:** Nguyen Hong Khoa
> **Mã Sinh Viên / Mã Học viên:** 02534
> **Chủ đề Lựa chọn:** Gợi ý 3.2 — Trợ lý Đơn hàng & Kho vận (Supply Chain Agent)

---

## 1. BẢNG CHẤM ĐIỂM AGENTIC FIT SCORING MATRIX (ĐÁNH GIÁ CHỦ ĐỀ)

| Tiêu chí Đánh giá | Mức độ (1 - 5) | Giải trình chi tiết lý do chọn điểm |
| :--- | :---: | :--- |
| **1. Multi-step Reasoning** | 4 / 5 | Với yêu cầu cập nhật có điều kiện, Agent phải đọc mã vận đơn, tra cứu trạng thái và vị trí lưu kho, rồi mới quyết định có thực hiện cập nhật hay không. Câu hỏi chỉ tra cứu thì ngắn hơn, nên không chấm tối đa. |
| **2. Tool Interaction** | 5 / 5 | Trạng thái đơn hàng và vị trí lưu kho phải lấy từ công cụ tra cứu; việc đổi trạng thái cần công cụ cập nhật. Chatbot chỉ sinh văn bản không thể xác nhận dữ liệu hiện tại hoặc ghi thay đổi. |
| **3. Dynamic Decision** | 5 / 5 | Kết quả tra cứu quyết định bước tiếp theo: đơn không tồn tại thì dừng và báo lỗi; trạng thái không thỏa điều kiện thì không cập nhật; trạng thái phù hợp thì mới gọi công cụ cập nhật. |
| **4. Long Horizon Goal** | 3 / 5 | Một đơn hàng đi qua nhiều trạng thái trong vòng đời giao nhận, nhưng phạm vi bài lab chủ yếu xử lý từng yêu cầu ngắn. Theo dõi dài hạn hoặc ghi nhớ giữa các phiên chưa phải chức năng được yêu cầu. |
| **TỔNG ĐIỂM AGENTIC FIT** | **17 / 20** | **Phù hợp với ReAct Agent** cho yêu cầu cần tra cứu rồi quyết định/cập nhật; câu hỏi hướng dẫn chung hoặc tra cứu đơn giản có thể xử lý bằng luồng ngắn hơn. Đây là đánh giá thiết kế, chưa phải kết quả nghiệm thu. |

---

## 2. TRÍCH XUẤT KẾT QUẢ WATERFALL TRACE LOG (SAU KHI CHẠY TEST SUITE TRÊN API THẬT)

> ⚠️ **YÊU CẦU NGHIỆM THU:** Mở tệp `.env` điền `GEMINI_API_KEY` (hoặc `OPENAI_API_KEY`) để kết nối LLM thật trước khi thực thi `python src/app.py --all`. Bài nộp chỉ dùng Mock Offline Provider sẽ không đạt điểm nghiệm thực tế.

**Trạng thái hiện tại của bài nộp:** `docs/trace_waterfall.json` là một lượt suite OpenAI cho đề tài 3.2, gồm 10 sự kiện (5 câu trả lời cuối, 5 lượt gọi tool) với các quyết định LLM đều `llm_live: true`. Các đoạn học vụ và Gemini bên dưới là ví dụ/lịch sử kiểm thử, không còn nằm trong file trace hiện tại.

Dưới đây là ví dụ học vụ có sẵn từ mẫu bài lab (không phải bằng chứng chạy live cho chủ đề 3.2):

```json
[
  {
    "step": 1,
    "action_type": "TOOL_EXECUTION",
    "tool_name": "academic_query",
    "arguments": {
      "student_id": "SV2026001"
    },
    "observation": {
      "status": "SUCCESS",
      "student_id": "SV2026001",
      "data": {
        "full_name": "Nguyễn Văn An",
        "gpa": 3.85
      }
    },
    "latency_ms": 120.5
  }
]
```

Đoạn trích **Gemini API thật** của TC04 từ bản trace trước khi chạy lại OpenAI (lịch sử kiểm thử, không thuộc file trace hiện tại; hai quyết định gọi công cụ đều có `llm_live: true`):

```json
[
  {
    "test_case_id": "TC04",
    "step": 1,
    "action_type": "TOOL_EXECUTION",
    "tool_name": "shipment_query",
    "arguments": {"tracking_id": "VD1002"},
    "observation": {"status": "SUCCESS", "tracking_id": "VD1002", "data": {"order_status": "Đang ở kho", "warehouse_location": "Kho Hà Nội - Kệ B2"}},
    "llm_live": true,
    "latency_ms": 4931.03
  },
  {
    "test_case_id": "TC04",
    "step": 2,
    "action_type": "TOOL_EXECUTION",
    "tool_name": "update_order_status",
    "arguments": {"tracking_id": "VD1002", "new_status": "Đang giao"},
    "observation": {"status": "SUCCESS", "tracking_id": "VD1002", "previous_status": "Đang ở kho", "new_status": "Đang giao"},
    "llm_live": true,
    "latency_ms": 5161.97
  }
]
```

---

## 3. TỔNG KẾT KẾT QUẢ NGHIỆM THU & NỘP BÀI

- [x] Đã điền API Key thật trong `.env` và xác nhận Agent gọi OpenAI API thật. Trước đó cũng đã thử Gemini API thật; hai ca Gemini từng fallback đã được chạy lại thành công, nhưng không dùng bản trace Gemini làm artifact hiện tại.
- **Tổng số Test Cases trong trace hiện tại:** 5 / 5 test cases (TC01–TC05 trong một lượt OpenAI liên tục).
- **Số lượt gọi Tool qua MCP Server trong trace hiện tại:** 5 lượt, tất cả có `llm_live: true`.
- **Chế độ tương tác:** OpenAI `--interactive --no-save` đã tra cứu VD1001 qua API thật, không có cảnh báo fallback.
- **Kết quả đẩy Repo nộp bài:** [x] Đã commit và push mã nguồn lên `origin/main` tại `https://github.com/hmster915/K4-DAY03-NguyenHongKhoa-02534`. Chưa nộp link trên VLearn.

---

> ✅ **HOÀN TẤT NỘP BÀI:** Sao chép đường link GitHub Repository cá nhân của bạn và dán vào ô nộp bài trên hệ thống LMS VLearn để hoàn tất Bài Lab 3!

---

## Kiểm thử phát triển ngoại tuyến (chưa phải nghiệm thu API thật)

Ngày 13/09/2026, bộ 5 test case của chủ đề 3.2 được chạy trong bộ nhớ với `MockOfflineProvider`, không ghi đè `docs/trace_waterfall.json`. Kết quả kiểm tra hành vi: **5/5 đạt**, tổng **5 lượt gọi công cụ**. Đây chỉ là kiểm thử phát triển; không điền các chỉ số nghiệm thu ở Mục 3 bằng số liệu Mock.

| Test case | Hành vi đã kiểm tra | Kết quả Mock |
| :--- | :--- | :---: |
| TC01 | Câu hỏi chung, không gọi công cụ | Đạt |
| TC02 | Tra cứu VD1001 qua `shipment_query` | Đạt |
| TC03 | Cập nhật VD1001 qua `update_order_status` | Đạt |
| TC04 | Tra cứu VD1002 rồi mới cập nhật khi trạng thái ở kho | Đạt |
| TC05 | VD9999 trả `NOT_FOUND`, không bịa trạng thái | Đạt |

Trace trong bộ nhớ có `thought`, `TOOL_EXECUTION`, `observation`, `FINAL_ANSWER`, `latency_ms` và đánh dấu `llm_live: false` cho các lượt gọi Mock. Tại thời điểm kiểm thử ngoại tuyến, Mục 2 và Mục 3 chưa có kết quả API thật; bằng chứng live được bổ sung riêng ở phía trên sau đó.

Đã kiểm tra thêm CLI bằng `python src/app.py --all --no-save` (thực thi 5/5 câu hỏi, 0 TODO) và `python src/app.py --interactive --no-save` (tra cứu VD1001 rồi thoát). Cả hai lệnh kết thúc thành công; mã băm của `docs/trace_waterfall.json` không đổi trước và sau khi chạy.

## Kiểm chứng API thật và giới hạn còn lại

- Trong lượt thử Gemini trước đây, `.env` dùng `gemini-3.6-flash`: model `gemini-2.5-flash` bị API trả 404 cho tài khoản này. API key không được ghi trong trace hoặc báo cáo.
- Bản trace lịch sử trước khi chạy lại OpenAI từng gồm 3 sự kiện học vụ cũ và 10 sự kiện Gemini được chọn cho TC01–TC05; 5 `TOOL_EXECUTION` Gemini đều có `llm_live: true`. TC01–TC03 lấy từ lượt suite; TC04–TC05 là lượt chạy lại riêng sau khi hai quyết định trong lượt suite đầu fallback về Mock. Bản này đã được thay bằng một lượt OpenAI liên tục trong file trace hiện tại.
- Chạy lại CLI `python src/app.py --all --no-save` với model đã sửa: hoàn tất 5/5 ca, 0 TODO, 5 lượt gọi tool, không có cảnh báo fallback trong lượt này. `--no-save` giữ nguyên bằng chứng đã ghép ở file trace.
- Trong lượt Gemini, chế độ `--interactive --no-save` nhận `429 RESOURCE_EXHAUSTED` do quota free tier rồi tự fallback về Mock; lượt đó **không** được tính là bằng chứng interactive live. OpenAI interactive đã được kiểm chứng riêng ở phần sau.
- `SHIPMENT_DATABASE` là dữ liệu minh họa trong bộ nhớ; Gemini chọn tool thật qua API, nhưng công cụ không kết nối một hãng vận chuyển hay hệ thống kho thực. Tại thời điểm kiểm thử Gemini, commit, push GitHub và nộp VLearn chưa được thực hiện.

## Kiểm chứng OpenAI sau khi đổi API key

Ngày 13/09/2026, cấu hình hiện tại trong `.env` là `LLM_PROVIDER=openai`, `LLM_MODEL=gpt-4o-mini`. Lượt thử OpenAI đầu tiên gọi API thật nhưng TC03 chọn nhầm `shipment_query` thay vì cập nhật. `src/app.py` được bổ sung giới hạn công cụ cho yêu cầu cập nhật trực tiếp, không thay đổi nhánh học vụ hoặc nhánh cập nhật có điều kiện. Sau sửa, **một lượt chạy mới** đạt TC01–TC05: 5/5 ca đúng hành vi, 5 lần `TOOL_EXECUTION` đều `llm_live: true`, không có cảnh báo fallback. TC04 tra cứu trước rồi mới cập nhật; TC05 trả `NOT_FOUND`.

Trích lược đúng các trường của sự kiện TC03 trong `docs/trace_waterfall.json` hiện tại:

```json
{
  "step": 1,
  "action_type": "TOOL_EXECUTION",
  "tool_name": "update_order_status",
  "arguments": {"tracking_id": "VD1001", "new_status": "Đang giao"},
  "observation": {"status": "SUCCESS", "tracking_id": "VD1001", "previous_status": "Đang ở kho", "new_status": "Đang giao"},
  "llm_live": true,
  "latency_ms": 1058.61
}
```

`docs/trace_waterfall.json` hiện chỉ chứa 10 sự kiện của một lượt suite OpenAI, không còn 3 sự kiện học vụ cũ hay 10 sự kiện Gemini. `python src/app.py --interactive --no-save` với OpenAI cũng tra cứu VD1001 thành công, không có cảnh báo fallback, rồi thoát bằng `exit`. Lượt Gemini interactive bị hết quota là lịch sử kiểm thử, không phải trạng thái nghiệm thu hiện tại. Đã push GitHub; chưa nộp link trên VLearn.

## Phase 7 — Self-audit trước khi nộp

- [x] Chủ đề 3.2 và bảng Agentic Fit 4 tiêu chí đã điền; `config/test_cases.json` có 5 ca và không còn câu hỏi TODO.
- [x] Tool schemas, MCP dispatch và ReAct loop chạy được; 5/5 ca trong trace OpenAI hiện tại đúng chuỗi hành động, 5 lượt tool live và 5 câu trả lời cuối.
- [x] CLI MCP, CLI suite và UI localhost đã được kiểm thử; UI chỉ dùng dữ liệu minh họa trong bộ nhớ và không ghi đè trace nộp bài.
- [ ] Môi trường đang dùng Python 3.14.5 theo lựa chọn cá nhân, ngoài dải 3.10–3.12 được README/CODELAB khuyến nghị; cần chấp nhận rủi ro tương thích khi chấm.
- [ ] Chưa xác nhận định dạng tên repo cuối cùng do tài liệu có hai quy ước (`K4-DAY03-...` và `K4B-DAY03-...` cho lớp chiều).
- [x] Đã xác nhận push `origin/main` lên GitHub.
- [ ] Chưa dán link repo vào LMS VLearn.

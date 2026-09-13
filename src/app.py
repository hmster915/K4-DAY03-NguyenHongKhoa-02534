"""
🚀 CORE AGENT APPLICATION (DAY 03: CHATBOT VS REACT AGENT)
Thực thi so sánh giữa Chatbot Baseline (Cấp 2) và ReAct Agent kết nối MCP Server (Cấp 3).
"""

import json
import os
import re
import sys
import time
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from mcp_server import MCPAcademicServer
from prompts import (
    CHATBOT_BASELINE_PROMPT,
    REACT_AGENT_SYSTEM_PROMPT,
    SUPPLY_CHAIN_AGENT_SYSTEM_PROMPT,
    MAX_ITERATIONS
)
from providers import get_llm_provider

load_dotenv()

def load_test_cases():
    """Tải danh sách 5 test cases từ config/test_cases.json hoặc config/test_cases.example.json"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "test_cases.json")
    if not os.path.exists(config_path):
        example_path = os.path.join(base_dir, "config", "test_cases.example.json")
        if os.path.exists(example_path):
            print("⚠️ [CONFIG NOTICE]: Chưa thấy file 'config/test_cases.json'. Đang dùng mẫu 'config/test_cases.example.json'.")
            print("👉 Hãy chạy: copy config/test_cases.example.json config/test_cases.json và viết test cases theo đề tài của bạn!\n")
            config_path = example_path
        else:
            config_path = "test_cases.json"
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_waterfall_trace(trace_data: list):
    """Ghi vết log Waterfall Trace Log ra file docs/trace_waterfall.json"""
    if "--no-save" in sys.argv:
        print("ℹ️ [OBSERVABILITY]: --no-save đang bật; không ghi đè trace hiện có.")
        return
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs_dir = os.path.join(base_dir, "docs")
    os.makedirs(docs_dir, exist_ok=True)
    trace_path = os.path.join(docs_dir, "trace_waterfall.json")
    with open(trace_path, "w", encoding="utf-8") as f:
        json.dump(trace_data, f, ensure_ascii=False, indent=2)
    print(f"📊 [OBSERVABILITY]: Đã lưu {len(trace_data)} sự kiện Waterfall Trace tại '{trace_path}'!")


def run_baseline_chatbot(user_query: str, provider):
    """Chạy Chatbot gốc (Cấp 2) không có công cụ gọi Tool"""
    print(f"\n💬 [CHATBOT BASELINE] Câu hỏi: {user_query}")
    response = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)
    print(f"🤖 Chatbot phản hồi:\n{response}")


def run_react_agent(user_query: str, provider, mcp_server: MCPAcademicServer) -> list:
    """
    [REACT AGENT LOOP] Thực thi vòng lặp Thought -> Action -> Observation với MCP Server
    Trả về danh sách trace log của phiên thực thi.
    """
    if "vận đơn" in user_query.lower() or re.search(r"\bVD\d+\b", user_query, re.IGNORECASE):
        return run_supply_chain_agent(user_query, provider, mcp_server)
    print(f"\n🤖 [REACT AGENT] Câu hỏi: {user_query}")
    
    step = 0
    trace_logs = []
    tools_list = [
        tool for tool in mcp_server.list_tools()
        if tool.get("name") in {"academic_query", "schedule_appointment"}
    ]
    
    while step < MAX_ITERATIONS:
        step += 1
        step_start_time = time.time()
        print(f"\n--- 🔄 Vòng lặp ReAct Loop (Step {step}/{MAX_ITERATIONS}) ---")
        
        # Gọi LLM với Native Tool Calling Specs
        llm_response = provider.generate_with_tools(user_query, tools_list, system_prompt=REACT_AGENT_SYSTEM_PROMPT)
        latency_ms = round((time.time() - step_start_time) * 1000, 2)
        
        thought = llm_response.get("thought", "Đang suy luận...")
        print(f"🧠 [Thought]: {thought}")
        
        # Trường hợp 1: LLM quyết định trả lời bằng văn bản trực tiếp
        if llm_response.get("type") == "text":
            final_content = llm_response.get("content", "")
            print(f"🏁 [Final Answer]: {final_content}")
            trace_logs.append({
                "step": step,
                "query": user_query,
                "action_type": "FINAL_ANSWER",
                "thought": thought,
                "output": final_content,
                "latency_ms": latency_ms
            })
            break
            
        # Trường hợp 2: LLM đề xuất gọi Tool (Action)
        elif llm_response.get("type") == "tool_call":
            tool_name = llm_response.get("tool_name")
            arguments = llm_response.get("arguments", {})
            
            print(f"🛠️ [Action Proposed]: {tool_name}({arguments})")
            
            # Thực thi Tool qua MCP Server
            mcp_result = mcp_server.call_tool(tool_name, arguments)
            obs_data = mcp_result.get("result", {})
            
            if not obs_data:
                print(f"👁️ [Observation từ MCP Server]: {{}}")
                print(f"⚠️ [CHÚ Ý]: MCP Server trả về kết quả rỗng! Học viên cần hoàn thành TODO 2.1 trong 'src/mcp_server.py'.")
                final_answer = "Chưa thể trả lời chi tiết do chưa nhận được dữ liệu từ MCP Server (hãy hoàn thành TODO 2.1)."
            else:
                obs_str = json.dumps(obs_data, ensure_ascii=False)
                print(f"👁️ [Observation từ MCP Server]: {obs_str}")
                
                # Tổng hợp Final Answer từ kết quả Observation thực tế
                if obs_data.get("status") == "SUCCESS":
                    if "data" in obs_data:
                        d = obs_data["data"]
                        final_answer = (
                            f"Kết quả tra cứu cho sinh viên {obs_data.get('student_id', '')} ({d.get('full_name', '')}): "
                            f"Lớp {d.get('class', '')}, GPA: {d.get('gpa', '')}, Email: {d.get('email', '')}, "
                            f"Trạng thái: {d.get('status', '')}, Cố vấn: {d.get('advisor', '')}."
                        )
                    elif "message" in obs_data:
                        final_answer = obs_data["message"]
                    else:
                        final_answer = f"Đã hoàn tất xử lý qua MCP Server: {json.dumps(obs_data, ensure_ascii=False)}"
                elif obs_data.get("status") == "NOT_FOUND":
                    final_answer = obs_data.get("message", "Không tìm thấy thông tin sinh viên yêu cầu.")
                else:
                    final_answer = f"Phản hồi từ công cụ: {json.dumps(obs_data, ensure_ascii=False)}"
            
            trace_logs.append({
                "step": step,
                "query": user_query,
                "action_type": "TOOL_EXECUTION",
                "tool_name": tool_name,
                "arguments": arguments,
                "observation": obs_data,
                "latency_ms": latency_ms
            })
            
            # Kết thúc vòng lặp sau khi hoàn tất Observation và xuất Final Answer
            print(f"🧠 [Thought]: Đã nhận được dữ liệu từ MCP Server. Tổng hợp kết quả phản hồi.")
            print(f"🏁 [Final Answer]: {final_answer}")
            
            trace_logs.append({
                "step": step + 1,
                "query": user_query,
                "action_type": "FINAL_ANSWER",
                "thought": "Tổng hợp kết quả từ MCP Server thành công.",
                "output": final_answer,
                "latency_ms": 10.0
            })
            break

    return trace_logs


def run_supply_chain_agent(user_query: str, provider, mcp_server: MCPAcademicServer) -> list:
    """Run the shipment ReAct loop without changing the starter academic path."""
    print(f"\n📦 [SUPPLY CHAIN AGENT] Câu hỏi: {user_query}")
    supply_tools = [
        tool for tool in mcp_server.list_tools()
        if tool.get("name") in {"shipment_query", "update_order_status"}
    ]
    lookup_tools = [tool for tool in supply_tools if tool["name"] == "shipment_query"]
    update_tools = [tool for tool in supply_tools if tool["name"] == "update_order_status"]
    conditional_update = "chỉ khi" in user_query.lower() and "cập nhật" in user_query.lower()
    tracking_match = re.search(r"\bVD\d+\b", user_query, re.IGNORECASE)
    requested_id = tracking_match.group(0).upper() if tracking_match else None
    target_match = re.search(r"(?:thành|sang)\s*['\"]?(Đang giao|Đã giao)", user_query, re.IGNORECASE)
    requested_status = target_match.group(1).lower() if target_match else None
    condition_match = re.search(r"chỉ khi.*?(Đang ở kho|Đang giao|Đã giao)", user_query, re.IGNORECASE)
    required_status = condition_match.group(1) if condition_match else None
    prompt = user_query
    trace_logs = []
    needs_update = False

    for step in range(1, MAX_ITERATIONS + 1):
        if conditional_update and (required_status is None or requested_status is None):
            answer = "Chưa xác định được điều kiện hoặc trạng thái đích; không cập nhật vận đơn."
            break
        available_tools = update_tools if needs_update else lookup_tools if conditional_update else supply_tools
        # For an explicit, unconditional status change, do not offer lookup as an alternative action.
        if not conditional_update and "cập nhật" in user_query.lower() and requested_status is not None:
            available_tools = update_tools
        step_start = time.time()
        response = provider.generate_with_tools(
            prompt, available_tools, system_prompt=SUPPLY_CHAIN_AGENT_SYSTEM_PROMPT
        )
        llm_live = bool(getattr(provider, "last_call_live", False))
        thought = response.get("thought", "Đang chọn bước tiếp theo.")
        response_type = response.get("type")

        if response_type == "text":
            answer = response.get("content", "") if not requested_id else "Chưa thể xác minh vận đơn vì mô hình không gọi công cụ tra cứu hoặc cập nhật."
            trace_logs.append({
                "step": step, "query": user_query, "action_type": "FINAL_ANSWER",
                "thought": thought, "output": answer,
                "llm_live": llm_live,
                "latency_ms": round((time.time() - step_start) * 1000, 2),
            })
            print(f"🏁 [Final Answer]: {answer}")
            return trace_logs

        if response_type != "tool_call":
            answer = "Không nhận được phản hồi hợp lệ từ mô hình."
            break

        tool_name = response.get("tool_name")
        arguments = response.get("arguments", {})
        allowed_names = {tool["name"] for tool in available_tools}
        if tool_name not in allowed_names or not isinstance(arguments, dict):
            answer = "Mô hình đề xuất công cụ hoặc tham số không hợp lệ; không thực thi."
            break
        if requested_id is None:
            answer = "Cần mã vận đơn cụ thể trước khi gọi công cụ."
            break
        if requested_id and str(arguments.get("tracking_id", "")).strip().upper() != requested_id:
            answer = "Mã vận đơn do mô hình đề xuất không khớp yêu cầu; không thực thi."
            break
        if tool_name == "update_order_status" and str(arguments.get("new_status", "")).lower() != requested_status:
            answer = "Trạng thái cập nhật không có trong yêu cầu; không thực thi."
            break

        mcp_result = mcp_server.call_tool(tool_name, arguments)
        observation = mcp_result.get("result", {})
        trace_logs.append({
            "step": step, "query": user_query, "action_type": "TOOL_EXECUTION",
            "thought": thought, "tool_name": tool_name, "arguments": arguments,
            "observation": observation,
            "llm_live": llm_live,
            "latency_ms": round((time.time() - step_start) * 1000, 2),
        })
        print(f"🛠️ [Action]: {tool_name}({arguments})")
        print(f"👁️ [Observation]: {json.dumps(observation, ensure_ascii=False)}")

        status = observation.get("status")
        if status != "SUCCESS":
            answer = observation.get("message") or observation.get("error") or "Công cụ không trả về dữ liệu hợp lệ."
            break

        if tool_name == "shipment_query":
            data = observation.get("data", {})
            current_status = data.get("order_status")
            warehouse = data.get("warehouse_location")
            if conditional_update:
                if current_status.lower() != required_status.lower():
                    answer = f"Vận đơn {requested_id} hiện ở trạng thái '{current_status}', không phải '{required_status}'; không cập nhật."
                    break
                needs_update = True
                prompt = (
                    f"Yêu cầu ban đầu: {user_query}\n"
                    f"Kết quả tra cứu từ MCP: {json.dumps(observation, ensure_ascii=False)}\n"
                    "Điều kiện đã được kiểm tra. Chỉ gọi công cụ cập nhật đúng mã vận đơn và trạng thái người dùng yêu cầu."
                )
                continue
            location_text = warehouse if warehouse else "không còn ở kho"
            answer = f"Vận đơn {observation.get('tracking_id')} đang ở trạng thái '{current_status}', vị trí lưu kho: {location_text}."
            break

        answer = observation.get("message", "Cập nhật đã được công cụ xác nhận.")
        break
    else:
        answer = f"Đã đạt giới hạn {MAX_ITERATIONS} bước mà chưa hoàn tất yêu cầu."
        step = MAX_ITERATIONS

    trace_logs.append({
        "step": step + 1, "query": user_query, "action_type": "FINAL_ANSWER",
        "thought": "Tổng hợp từ kết quả công cụ hoặc thông báo lỗi.",
        "output": answer, "latency_ms": 0.0,
    })
    print(f"🏁 [Final Answer]: {answer}")
    return trace_logs


if __name__ == "__main__":
    print("==========================================================")
    print("🏫 VINUNI AI COURSE - DAY 03 LAB: CHATBOT VS REACT AGENT")
    print("==========================================================")
    
    provider = get_llm_provider()
    mcp_server = MCPAcademicServer()
    
    print(f"🔌 LLM Provider: {provider.__class__.__name__}")
    print(f"🌐 MCP Server: {mcp_server.server_name}\n")
    
    tests = load_test_cases()
    print(f"✅ Đã tải thành công {len(tests)} Test Cases thử nghiệm.\n")
    
    if "--interactive" in sys.argv:
        print("🎮 [INTERACTIVE MODE] Trò chuyện trực tiếp với ReAct Agent:")
        print("💡 Gợi ý câu hỏi thử nghiệm:")
        print("   - Câu hỏi chung: 'Quy chế học vụ VinUni yêu cầu bao nhiêu tín chỉ?'")
        print("   - Tra cứu học vụ: 'Hãy tra cứu thông tin học vụ của sinh viên SV2026001'")
        print("   - Đặt lịch hẹn: 'Đặt lịch hẹn tư vấn cho SV2026001 vào 14:00 ngày 15/09/2026'")
        print("   - Gõ 'exit' hoặc 'quit' để kết thúc phiên trò chuyện.\n")
        while True:
            try:
                user_input = input("👤 Sinh viên hỏi: ").strip()
                if not user_input or user_input.lower() in ["exit", "quit"]:
                    print("👋 Tạm biệt! Kết thúc phiên trò chuyện.")
                    break
                logs = run_react_agent(user_input, provider, mcp_server)
                save_waterfall_trace(logs)
            except (KeyboardInterrupt, EOFError):
                print("\n👋 Đã thoát phiên tương tác.")
                break
    elif "--all" in sys.argv:
        print("🚀 [TEST SUITE MODE] Kiểm tra 5 Test Cases:")
        completed_count = 0
        todo_count = 0
        all_traces = []
        
        for tc in tests:
            print(f"\n==================================================")
            print(f"🧪 [{tc['id']}] Loại test: {tc['type']} (Độ phức tạp: {tc['complexity']})")
            print(f"📌 Kỳ vọng: {tc['expected_behavior']}")
            
            if tc["question"].strip().startswith("TODO"):
                print(f"⏸️ [CHƯA KÍCH HOẠT - ĐANG LÀ TODO]:")
                print(f"   {tc['question']}")
                print(f"   👉 Hãy mở file 'config/test_cases.json' để viết câu hỏi thực tế cho Test Case này!")
                todo_count += 1
            else:
                logs = run_react_agent(tc["question"], provider, mcp_server)
                all_traces.extend(logs)
                completed_count += 1
                
        print(f"\n==================================================")
        print(f"📊 [KẾT QUẢ TEST SUITE]: Đã thực thi {completed_count}/{len(tests)} Test Cases | {todo_count} Test Cases đang chờ điền câu hỏi (TODO)")
        if all_traces:
            save_waterfall_trace(all_traces)
        print(f"💡 Để trò chuyện trực tiếp từng câu: Chạy 'python src/app.py --interactive'")
    else:
        # Chế độ mặc định khi chỉ gõ 'python src/app.py'
        print("ℹ️ HƯỚNG DẪN SỬ DỤNG CHƯƠNG TRÌNH:")
        print("  1. Chat trực tiếp liên tục:   python src/app.py --interactive")
        print("  2. Chạy toàn bộ Test Cases:    python src/app.py --all\n")
        
        sample_query = tests[1]["question"]
        print(f"--- 🏁 DEMO CHẠY THỬ 1 TEST CASE MẪU (TC02: Tra cứu học vụ) ---")
        logs = run_react_agent(sample_query, provider, mcp_server)
        save_waterfall_trace(logs)
        print("\n💡 Hãy thử ngay lệnh: python src/app.py --interactive để chat trực tiếp!")

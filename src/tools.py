"""
🛠️ TOOL DEFINITIONS & EXECUTION BACKEND
Mã nguồn chứa danh sách Tool Schemas (JSON Schema) và Execution Layer phục vụ cho MCP Server.
"""

import json
from typing import Dict, Any

# ==============================================================================
# 1. KHAI BÁO TOOL SCHEMAS CHUẨN NATIVE JSON SCHEMA (TASK 1.2)
# ==============================================================================

TOOLS_SCHEMA = [
    # Tool 1: Đã được định nghĩa mẫu sẵn cho Học viên tham khảo
    {
        "name": "academic_query",
        "description": "Tra cứu hồ sơ và thông tin học vụ của sinh viên VinUni bằng mã sinh viên.",
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {
                    "type": "string",
                    "description": "Mã sinh viên cần tra cứu (ví dụ: 'SV2026001')"
                }
            },
            "required": ["student_id"]
        }
    },
    
    # --------------------------------------------------------------------------
    # TASK 1.2: TOOL SCHEMA CHO 'schedule_appointment' ĐÃ HOÀN THIỆN
    # 🎯 YÊU CẦU THIẾT KẾ SCHEMA (JSON SCHEMA STANDARD):
    # 1. Tool dùng để đặt lịch hẹn tư vấn học vụ với Cố vấn học tập VinUni.
    # 2. Thiết kế các tham số (properties) để LLM trích xuất:
    #    - student_id (string): Mã sinh viên cần đặt lịch (ví dụ: 'SV2026001')
    #    - datetime_str (string): Thời gian hẹn (ví dụ: '14:00 15/09/2026')
    #    - advisor_name (string): Tên cố vấn học tập
    # 3. Khai báo danh sách các trường bắt buộc (required).
    # --------------------------------------------------------------------------
    {
        "name": "schedule_appointment",
        "description": "Đặt lịch hẹn tư vấn học vụ với Cố vấn học tập VinUni.",
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {
                    "type": "string",
                    "description": "Mã sinh viên cần đặt lịch (ví dụ: 'SV2026001')"
                },
                "datetime_str": {
                    "type": "string",
                    "description": "Thời gian hẹn (ví dụ: '14:00 15/09/2026')"
                },
                "advisor_name": {
                    "type": "string",
                    "description": "Tên cố vấn học tập cần đặt lịch"
                }
            },
            "required": ["student_id", "datetime_str", "advisor_name"]
        }
    }
]

# Công cụ bổ sung cho đề tài 3.2; hai công cụ mẫu học vụ ở trên được giữ nguyên.
TOOLS_SCHEMA += [
    {
        "name": "shipment_query",
        "description": (
            "Tra cứu trạng thái đơn hàng và vị trí lưu kho hiện tại bằng mã vận đơn. "
            "Dùng công cụ này trước khi cập nhật có điều kiện."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "tracking_id": {
                    "type": "string",
                    "description": "Mã vận đơn cần tra cứu, ví dụ VD1001.",
                }
            },
            "required": ["tracking_id"],
        },
    },
    {
        "name": "update_order_status",
        "description": (
            "Cập nhật trạng thái của một vận đơn đã xác định. "
            "Chỉ gọi khi người dùng yêu cầu cập nhật và điều kiện của họ được đáp ứng."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "tracking_id": {
                    "type": "string",
                    "description": "Mã vận đơn cần cập nhật, ví dụ VD1001.",
                },
                "new_status": {
                    "type": "string",
                    "description": "Trạng thái mới của đơn hàng.",
                    "enum": ["Đang giao", "Đã giao"],
                },
            },
            "required": ["tracking_id", "new_status"],
        },
    },
]

# ==============================================================================
# 2. MÔ PHỎNG DỮ LIỆU & HÀM THỰC THI TOOL (EXECUTION LAYER)
# ==============================================================================

MOCK_DATABASE = {
    "SV2026001": {
        "full_name": "Nguyễn Văn An",
        "class": "AI-K4",
        "gpa": 3.85,
        "email": "an.nv@vinuni.edu.vn",
        "status": "Đang học",
        "advisor": "PGS.TS Nguyễn Văn A"
    },
    "SV2026002": {
        "full_name": "Trần Thị Bình",
        "class": "AI-K4",
        "gpa": 3.60,
        "email": "binh.tt@vinuni.edu.vn",
        "status": "Đang học",
        "advisor": "TS. Lê Thị B"
    }
}


def execute_academic_query(student_id: str) -> str:
    """Thực thi tra cứu học vụ theo mã sinh viên"""
    student = MOCK_DATABASE.get(student_id.strip().upper())
    if student:
        return json.dumps({
            "status": "SUCCESS",
            "student_id": student_id,
            "data": student
        }, ensure_ascii=False)
    else:
        return json.dumps({
            "status": "NOT_FOUND",
            "message": f"Không tìm thấy dữ liệu sinh viên có mã '{student_id}'"
        }, ensure_ascii=False)


def execute_schedule_appointment(student_id: str, datetime_str: str, advisor_name: str = "PGS.TS Nguyễn Văn A") -> str:
    """Thực thi đặt lịch hẹn tư vấn học vụ"""
    return json.dumps({
        "status": "SUCCESS",
        "booking_id": f"BK-{student_id}-99",
        "student_id": student_id,
        "datetime": datetime_str,
        "advisor": advisor_name,
        "message": f"Đặt lịch thành công cho sinh viên {student_id} với {advisor_name} vào lúc {datetime_str}."
    }, ensure_ascii=False)


# Dữ liệu minh họa nội bộ; không phải hệ thống vận đơn thực tế.
SHIPMENT_DATABASE = {
    "VD1001": {
        "order_status": "Đang ở kho",
        "warehouse_location": "Kho Hà Nội - Kệ A1",
    },
    "VD1002": {
        "order_status": "Đang ở kho",
        "warehouse_location": "Kho Hà Nội - Kệ B2",
    },
}

ALLOWED_TRANSITIONS = {
    "Đang ở kho": {"Đang giao"},
    "Đang giao": {"Đã giao"},
    "Đã giao": set(),
}


def execute_shipment_query(tracking_id: str) -> str:
    """Return the mock order status and current warehouse location."""
    normalized_id = tracking_id.strip().upper()
    if not normalized_id:
        return json.dumps({"status": "INVALID_ARGUMENT", "message": "Mã vận đơn không được để trống."}, ensure_ascii=False)

    shipment = SHIPMENT_DATABASE.get(normalized_id)
    if shipment is None:
        return json.dumps({
            "status": "NOT_FOUND",
            "tracking_id": normalized_id,
            "message": f"Không tìm thấy vận đơn '{normalized_id}'.",
        }, ensure_ascii=False)

    return json.dumps({
        "status": "SUCCESS",
        "tracking_id": normalized_id,
        "data": shipment.copy(),
    }, ensure_ascii=False)


def execute_update_order_status(tracking_id: str, new_status: str) -> str:
    """Apply a valid status transition to the in-memory mock database."""
    normalized_id = tracking_id.strip().upper()
    if not normalized_id:
        return json.dumps({"status": "INVALID_ARGUMENT", "message": "Mã vận đơn không được để trống."}, ensure_ascii=False)

    shipment = SHIPMENT_DATABASE.get(normalized_id)
    if shipment is None:
        return json.dumps({
            "status": "NOT_FOUND",
            "tracking_id": normalized_id,
            "message": f"Không tìm thấy vận đơn '{normalized_id}'.",
        }, ensure_ascii=False)

    requested_status = new_status.strip()
    current_status = shipment["order_status"]
    if requested_status not in ALLOWED_TRANSITIONS.get(current_status, set()):
        return json.dumps({
            "status": "INVALID_TRANSITION",
            "tracking_id": normalized_id,
            "current_status": current_status,
            "requested_status": requested_status,
            "message": f"Không thể chuyển vận đơn '{normalized_id}' từ '{current_status}' sang '{requested_status}'.",
        }, ensure_ascii=False)

    shipment["order_status"] = requested_status
    shipment["warehouse_location"] = None
    return json.dumps({
        "status": "SUCCESS",
        "tracking_id": normalized_id,
        "previous_status": current_status,
        "new_status": requested_status,
        "message": f"Đã cập nhật vận đơn '{normalized_id}' từ '{current_status}' sang '{requested_status}'.",
    }, ensure_ascii=False)


# Router gọi tool thực tế
TOOL_ROUTER = {
    "academic_query": execute_academic_query,
    "schedule_appointment": execute_schedule_appointment
}

TOOL_ROUTER.update({
    "shipment_query": execute_shipment_query,
    "update_order_status": execute_update_order_status,
})


def dispatch_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Hàm trung chuyển thực thi tool"""
    if tool_name in TOOL_ROUTER:
        try:
            return TOOL_ROUTER[tool_name](**arguments)
        except Exception as e:
            return json.dumps({"status": "EXECUTION_ERROR", "error": str(e)}, ensure_ascii=False)
    return json.dumps({"status": "UNKNOWN_TOOL", "error": f"Tool '{tool_name}' không tồn tại!"}, ensure_ascii=False)

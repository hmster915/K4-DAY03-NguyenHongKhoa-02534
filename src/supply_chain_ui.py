"""Local web UI for topic 3.2; keeps the lab CLI and trace artifacts unchanged."""

import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

from app import run_supply_chain_agent
from mcp_server import MCPAcademicServer
from providers import get_llm_provider


PAGE = """<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Supply Chain Agent · Lab 3</title>
  <style>
    :root { color-scheme: light; font-family: system-ui, -apple-system, Segoe UI, sans-serif; }
    * { box-sizing: border-box; }
    body { margin: 0; background: #f2f5f8; color: #122234; }
    header { background: #102b46; color: white; padding: 28px max(24px, calc((100vw - 1080px)/2)); }
    h1 { margin: 0 0 6px; font-size: 1.8rem; }
    header p { margin: 0; color: #c8d9e8; }
    main { max-width: 1080px; margin: 26px auto; padding: 0 24px 40px; display: grid; gap: 18px; }
    .card { background: white; border: 1px solid #dbe4ec; border-radius: 14px; padding: 20px; box-shadow: 0 3px 14px #102b4609; }
    h2 { font-size: 1.1rem; margin: 0 0 14px; }
    .meta, .samples { display: flex; flex-wrap: wrap; gap: 8px; }
    .pill { background: #e8f1f8; color: #174569; border-radius: 100px; padding: 6px 11px; font-size: .88rem; }
    .samples button { background: #f4f8fb; color: #16476a; border: 1px solid #c8d9e8; border-radius: 9px; padding: 9px 12px; cursor: pointer; }
    .samples button:hover, .samples button:focus-visible { background: #dcebf5; }
    textarea { width: 100%; min-height: 105px; resize: vertical; border: 1px solid #aabecd; border-radius: 10px; padding: 12px; font: inherit; line-height: 1.5; }
    textarea:focus { outline: 2px solid #3a8abd; outline-offset: 1px; }
    .row { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-top: 12px; }
    .primary { border: 0; border-radius: 10px; background: #0d6e91; color: white; padding: 10px 18px; font: inherit; font-weight: 650; cursor: pointer; }
    .primary:disabled { opacity: .55; cursor: wait; }
    .muted { color: #536878; font-size: .9rem; }
    .answer { white-space: pre-wrap; line-height: 1.65; min-height: 30px; }
    .notice { margin-top: 12px; padding: 10px 12px; border-radius: 8px; background: #fff1d9; color: #715218; }
    .success { background: #e2f5e9; color: #196038; }
    .trace-item { border-left: 3px solid #8ca9bd; padding: 8px 14px; margin: 10px 0; background: #f7fafc; border-radius: 0 8px 8px 0; }
    .trace-item strong { display: inline-block; margin-right: 8px; }
    pre { white-space: pre-wrap; overflow-wrap: anywhere; margin: 8px 0 0; font-size: .84rem; }
    .error { color: #9f2b2b; }
    @media (max-width: 600px) { header { padding: 22px 24px; } .row { align-items: flex-start; flex-direction: column; } }
  </style>
</head>
<body>
  <header><h1>📦 Supply Chain Agent</h1><p>Lab 3 · Đề tài 3.2: tra cứu vận đơn, vị trí kho và cập nhật trạng thái</p></header>
  <main>
    <section class="card">
      <h2>Phiên thử nghiệm</h2>
      <div id="meta" class="meta" aria-live="polite"><span class="pill">Đang tải cấu hình…</span></div>
      <p class="muted">Dữ liệu vận đơn là minh họa trong bộ nhớ. Cập nhật chỉ tồn tại cho đến khi dừng máy chủ UI.</p>
    </section>
    <section class="card">
      <h2>Thử nhanh 5 trường hợp</h2>
      <div class="samples">
        <button type="button" data-case="0">TC01 · Câu hỏi chung</button>
        <button type="button" data-case="1">TC02 · Tra cứu VD1001</button>
        <button type="button" data-case="2">TC03 · Cập nhật VD1001</button>
        <button type="button" data-case="3">TC04 · Tra cứu rồi cập nhật VD1002</button>
        <button type="button" data-case="4">TC05 · Không tìm thấy</button>
      </div>
    </section>
    <section class="card">
      <h2>Gửi yêu cầu</h2>
      <form id="chat-form">
        <label for="question" class="muted">Câu hỏi về vận đơn</label>
        <textarea id="question" required maxlength="4000" placeholder="Ví dụ: Tra cứu trạng thái và vị trí lưu kho của vận đơn VD1001."></textarea>
        <div class="row"><span class="muted">Mỗi yêu cầu có thể gọi API và tốn quota.</span><button id="send" class="primary" type="submit">Gửi yêu cầu</button></div>
      </form>
    </section>
    <section class="card" aria-live="polite">
      <h2>Kết quả</h2>
      <div id="answer" class="answer muted">Chọn một trường hợp thử hoặc nhập câu hỏi.</div>
      <div id="live-status"></div>
    </section>
    <section class="card">
      <h2>Waterfall trace của yêu cầu này</h2>
      <div id="trace" class="muted">Chưa có sự kiện.</div>
    </section>
  </main>
  <script>
    const prompts = [
      "Mã vận đơn dùng để làm gì khi tra cứu đơn hàng?",
      "Tra cứu trạng thái và vị trí lưu kho của vận đơn VD1001.",
      "Cập nhật trạng thái vận đơn VD1001 thành 'Đang giao'.",
      "Tra cứu vận đơn VD1002. Chỉ khi kết quả cho thấy đơn đang ở kho, hãy cập nhật trạng thái thành 'Đang giao'; nếu không, cho tôi biết lý do và giữ nguyên trạng thái.",
      "Tra cứu trạng thái và vị trí lưu kho của vận đơn VD9999."
    ];
    const question = document.getElementById("question");
    const answer = document.getElementById("answer");
    const trace = document.getElementById("trace");
    const liveStatus = document.getElementById("live-status");
    const send = document.getElementById("send");
    document.querySelectorAll("[data-case]").forEach(button => {
      button.addEventListener("click", () => { question.value = prompts[Number(button.dataset.case)]; question.focus(); });
    });
    fetch("/api/meta").then(r => r.json()).then(data => {
      const meta = document.getElementById("meta"); meta.replaceChildren();
      ["Provider: " + data.provider, "Model: " + data.model, "MCP: " + data.server].forEach(label => {
        const span = document.createElement("span"); span.className = "pill"; span.textContent = label; meta.append(span);
      });
    }).catch(() => { document.getElementById("meta").textContent = "Không đọc được cấu hình máy chủ."; });
    document.getElementById("chat-form").addEventListener("submit", async event => {
      event.preventDefault(); send.disabled = true; answer.className = "answer muted"; answer.textContent = "Đang xử lý…";
      trace.replaceChildren(); liveStatus.replaceChildren();
      try {
        const response = await fetch("/api/chat", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ question: question.value }) });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Yêu cầu không thành công.");
        answer.className = "answer"; answer.textContent = data.answer || "Không có câu trả lời.";
        const notice = document.createElement("div"); notice.className = data.live ? "notice success" : "notice";
        notice.textContent = data.live ? "Quyết định LLM: API thật." : "Lưu ý: lượt này dùng Mock/fallback hoặc không xác minh được API thật.";
        liveStatus.append(notice);
        data.trace.forEach(item => {
          const box = document.createElement("div"); box.className = "trace-item";
          const title = document.createElement("strong");
          title.textContent = "Bước " + item.step + " · " + item.action_type + (item.tool_name ? " · " + item.tool_name : "");
          box.append(title);
          if (Object.hasOwn(item, "llm_live")) {
            const tag = document.createElement("span"); tag.className = "muted"; tag.textContent = item.llm_live ? "LIVE" : "MOCK/FALLBACK"; box.append(tag);
          }
          const details = document.createElement("pre");
          details.textContent = JSON.stringify({ thought: item.thought, arguments: item.arguments, observation: item.observation, output: item.output, latency_ms: item.latency_ms }, null, 2);
          box.append(details); trace.append(box);
        });
      } catch (error) { answer.className = "answer error"; answer.textContent = error.message; }
      finally { send.disabled = false; }
    });
  </script>
</body>
</html>
"""


def make_handler(provider, mcp_server):
    """Build one local HTTP handler around the current in-memory shipment state."""

    class SupplyChainHandler(BaseHTTPRequestHandler):
        def send_json(self, status, payload):
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path == "/":
                body = PAGE.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(body)
            elif self.path == "/api/meta":
                self.send_json(200, {
                    "provider": type(provider).__name__,
                    "model": getattr(provider, "model_name", "unknown"),
                    "server": mcp_server.server_name,
                })
            else:
                self.send_json(404, {"error": "Không tìm thấy đường dẫn."})

        def do_POST(self):
            if self.path != "/api/chat":
                self.send_json(404, {"error": "Không tìm thấy đường dẫn."})
                return
            if self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower() != "application/json":
                self.send_json(415, {"error": "Chỉ nhận Content-Type: application/json."})
                return
            origin = self.headers.get("Origin")
            if origin and origin != f"http://127.0.0.1:{self.server.server_port}":
                self.send_json(403, {"error": "Chỉ nhận yêu cầu từ UI localhost."})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                self.send_json(400, {"error": "Content-Length không hợp lệ."})
                return
            if length < 1 or length > 8192:
                self.send_json(413, {"error": "Yêu cầu rỗng hoặc quá dài."})
                return
            try:
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                self.send_json(400, {"error": "Cần gửi JSON UTF-8 hợp lệ."})
                return
            if not isinstance(payload, dict) or not isinstance(payload.get("question"), str):
                self.send_json(400, {"error": "Thiếu câu hỏi dạng văn bản."})
                return
            question = payload["question"].strip()
            if not question or len(question) > 4000:
                self.send_json(400, {"error": "Câu hỏi phải có từ 1 đến 4000 ký tự."})
                return
            try:
                trace = run_supply_chain_agent(question, provider, mcp_server)
                answer = next((event.get("output", "") for event in reversed(trace)
                               if event.get("action_type") == "FINAL_ANSWER"), "")
                decisions = [event["llm_live"] for event in trace if "llm_live" in event]
                self.send_json(200, {
                    "answer": answer,
                    "trace": trace,
                    "live": bool(decisions) and all(decisions),
                })
            except Exception:
                # Keep API keys and provider exception details out of browser responses.
                self.send_json(500, {"error": "Lỗi xử lý yêu cầu. Xem terminal của UI để chẩn đoán."})
                raise

    return SupplyChainHandler


def main():
    parser = argparse.ArgumentParser(description="Local UI for Lab 3 Supply Chain Agent")
    parser.add_argument("--port", type=int, default=8765, help="Localhost port (default: 8765)")
    args = parser.parse_args()
    provider = get_llm_provider()
    mcp_server = MCPAcademicServer(server_name="supply-chain-lab-mcp-server")
    server = HTTPServer(("127.0.0.1", args.port), make_handler(provider, mcp_server))
    print(f"Supply Chain UI: http://127.0.0.1:{server.server_port}")
    print(f"Provider: {type(provider).__name__} | Model: {getattr(provider, 'model_name', 'unknown')}")
    print("Press Ctrl+C to stop. Shipment updates reset when this process restarts.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Supply Chain UI.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()

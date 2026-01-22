import re


def clean_markdown_string(text: str) -> str:
    "Loại bỏ các text không cần thiết ví dụ như ``` hoặc ```markdown chỉ giữ lại markdown"
    if not text:
        return ""
    # Tìm tất cả các đoạn code block
    code_blocks = re.findall(r"```(.*?)```", text, re.DOTALL)
    if code_blocks:
        return "\n".join(code_blocks)
    return text


def clean_json_string(text: str) -> str:
    """Trích xuất chuỗi JSON từ text, hỗ trợ cả {} và []"""
    if not text:
        return ""
    # Tìm cặp ngoặc ngoài cùng (bao quát cả Object và Array)
    match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
    return match.group(0) if match else text

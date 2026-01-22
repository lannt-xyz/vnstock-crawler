import re


def clean_markdown_string(text: str) -> str:
    "Loại bỏ các text không cần thiết ví dụ như ``` hoặc ```markdown chỉ giữ lại markdown"
    if not text:
        return ""
    # Loại bỏ ```markdown hoặc ``` ở đầu và cuối chuỗi
    text = re.sub(r"^```(markdown)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    # Thay thế `\n` bằng newline thực sự
    text = text.replace("\\n", "\n")
    # Nếu có chứa qoute ở đầu và cuối, loại bỏ nó
    if text.startswith('"') and text.endswith('"'):
        text = text[1:-1].strip()

    return text.strip()


def clean_json_string(text: str) -> str:
    """Trích xuất chuỗi JSON từ text, hỗ trợ cả {} và []"""
    if not text:
        return ""
    # Tìm cặp ngoặc ngoài cùng (bao quát cả Object và Array)
    match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
    return match.group(0) if match else text

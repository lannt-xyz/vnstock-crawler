import json
import itertools
import re
import time

from google.genai import Client, types
from typing import Union, Dict, List
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.logger import logger
from app.config import config

class GeminiRotator:
    def __init__(self, api_keys: List[str], model_id: str, delay_seconds: float = 1.0):
        self.key_pool = itertools.cycle(api_keys)
        self.model_id = model_id
        self.delay_seconds = delay_seconds
        self.last_request_time = 0

    def get_client(self):
        # Tính toán delay để tránh bị rate limit IP
        now = time.time()
        elapsed = now - self.last_request_time
        if elapsed < self.delay_seconds:
            time.sleep(self.delay_seconds - elapsed)
        
        current_key = next(self.key_pool)
        # genai.configure(api_key=current_key)
        client = Client(api_key=current_key)
        
        self.last_request_time = time.time()
        return client

rotator = GeminiRotator(
    api_keys=config.GEMINI_API_KEYS, 
    model_id=config.GEMINI_MODEL_ID,
    delay_seconds=1.5  # Nghỉ 1.5s giữa mỗi lần lấy key
)

def clean_json_string(text: str) -> str:
    """Trích xuất chuỗi JSON từ text, hỗ trợ cả {} và []"""
    if not text:
        return ""
    # Tìm cặp ngoặc ngoài cùng (bao quát cả Object và Array)
    match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
    return match.group(0) if match else text

@retry(
    stop=stop_after_attempt(len(config.GEMINI_API_KEYS,) * 2),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(Exception),
    reraise=True # Giúp bạn thấy lỗi thật sự sau khi đã thử hết số lần
)
def extract_data(prompt: str) -> Union[Dict, List]:
    client = rotator.get_client()
    
    try:
        response = client.models.generate_content(
            model=rotator.model_id,
            contents=types.Part.from_text(text=prompt),
            config={
                'temperature': 0,
                'top_p': 0.95,
                'top_k': 20,
            },
        )
        
        # KIỂM TRA AN TOÀN: Tránh lỗi attribute .text khi response bị block
        if not response.candidates or not response.candidates[0].content.parts:
            # Nếu bị block bởi Safety Filter, ta nên raise lỗi để retry đổi key/prompt
            logger.warning("Gemini response was blocked by safety filters or empty.")
            raise ValueError("Empty or blocked response from Gemini")

        response_text = response.text
        
        # Bóc tách JSON
        json_str = clean_json_string(response_text).strip()
        return json.loads(json_str)

    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Format error: {e}. Retrying...")
        raise e # Kích hoạt retry
    except Exception as e:
        logger.error(f"API Error with key: {str(e)[:100]}")
        raise e # Kích hoạt retry
    finally:
        client.close()

import requests
import os
from dotenv import load_dotenv

load_dotenv()

class LMStudioService:
    def __init__(self):
        self.base_url = os.getenv("LM_STUDIO_URL", "http://localhost:1234")
    
    def generate_response(self, prompt: str, context: str = "") -> str:
        """
        Gửi request tới LM Studio với Phi-4 Mini
        """
        # Cấu hình prompt cho educational context
        system_prompt = """Bạn là Hannah, một AI assistant chuyên hỗ trợ sinh viên học phần mềm. 
        Hãy trả lời chính xác, ngắn gọn và có ví dụ cụ thể khi cần thiết."""
        
        if context:
            full_prompt = f"{system_prompt}\n\nTài liệu tham khảo:\n{context}\n\nCâu hỏi: {prompt}\n\nTrả lời:"
        else:
            full_prompt = f"{system_prompt}\n\nCâu hỏi: {prompt}\n\nTrả lời:"
        
        try:
            # API call tới LM Studio
            response = requests.post(
                f"{self.base_url}/v1/completions",
                json={
                    "prompt": full_prompt,
                    "max_tokens": 512,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "stop": ["</s>", "\n\n"]
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["text"].strip()
            else:
                return f"Lỗi kết nối LM Studio: {response.status_code}"
                
        except Exception as e:
            return f"Lỗi: {str(e)}"

llm_service = LMStudioService()
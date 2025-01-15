from typing import Dict, Tuple
import openai
from openai import AsyncOpenAI, OpenAIError
import tiktoken
import os
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
            
        self.client = AsyncOpenAI(api_key=api_key)
        self.models_config = {
            "gpt-3.5-turbo": {"cost_per_1k_tokens": 0.0015},
            "gpt-4": {"cost_per_1k_tokens": 0.03},
        }

    def count_tokens(self, text: str, model: str = "gpt-3.5-turbo") -> int:
        """Verilen metin için token sayısını hesapla"""
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int, model: str) -> float:
        """Token kullanımına göre maliyeti hesapla"""
        if model not in self.models_config:
            raise ValueError(f"Model {model} desteklenmiyor")
        
        total_tokens = prompt_tokens + completion_tokens
        cost_per_1k = self.models_config[model]["cost_per_1k_tokens"]
        return (total_tokens / 1000) * cost_per_1k

    async def call_model(self, prompt: str, model: str = "gpt-3.5-turbo", temperature: float = 0.7) -> Tuple[str, Dict]:
        """Model çağrısı yap ve sonuçları döndür"""
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature
            )
            
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
                "cost_usd": self.calculate_cost(
                    response.usage.prompt_tokens,
                    response.usage.completion_tokens,
                    model
                )
            }
            
            output_text = response.choices[0].message.content
            return output_text, usage
            
        except OpenAIError as e:
            raise Exception(f"OpenAI API hatası: {str(e)}")
        except Exception as e:
            raise Exception(f"Model çağrısı başarısız: {str(e)}")

    async def optimize_prompt(self, current_prompt: str) -> Tuple[str, Dict]:
        """Promptu optimize et"""
        optimization_prompt = f"""
        Aşağıdaki promptu daha kısa ve net hale getir. 
        Gereksiz kelimeleri çıkar ve maksimum 50 kelime olacak şekilde düzenle:

        {current_prompt}
        """
        return await self.call_model(optimization_prompt) 
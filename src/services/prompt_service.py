from typing import Dict, Optional
from datetime import datetime
from bson import ObjectId

from ..models.llm_client import LLMClient
from ..models.lime_analyzer import LIMEAnalyzer
from ..database.mongodb import MongoDB
from ..utils.logger import logger

class PromptService:
    def __init__(self):
        self.llm_client = LLMClient()
        self.db = MongoDB()
        self.lime_analyzer = LIMEAnalyzer()
        
    async def create_prompt(self, text: str, model_name: str = "gpt-3.5-turbo", temperature: float = 0.7) -> Dict:
        """Yeni bir prompt oluştur ve ilk model yanıtını al"""
        try:
            # Model yanıtı al
            output_text, usage = await self.llm_client.call_model(text, model_name, temperature)
            
            # Veritabanı kaydı oluştur
            prompt_data = {
                "original_prompt": text,
                "model_responses": [{
                    "iteration": 1,
                    "prompt_text": text,
                    "model_name": model_name,
                    "completion_text": output_text,
                    **usage,
                    "timestamp": datetime.utcnow().isoformat()
                }],
                "status": "completed",
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Veritabanına kaydet
            prompt_id = await self.db.create_prompt(prompt_data)
            
            logger.info(f"Yeni prompt oluşturuldu", extra={
                "prompt_id": str(prompt_id),
                "model": model_name,
                "tokens": usage["total_tokens"]
            })
            
            return {"prompt_id": str(prompt_id), **prompt_data}
            
        except Exception as e:
            logger.error(f"Prompt oluşturma hatası: {str(e)}")
            raise
            
    async def optimize_prompt(self, prompt_id: str) -> Dict:
        """Var olan bir promptu optimize et"""
        try:
            # Mevcut promptu getir
            prompt_data = await self.db.get_prompt(prompt_id)
            if not prompt_data:
                raise ValueError(f"Prompt bulunamadı: {prompt_id}")
                
            original_prompt = prompt_data["original_prompt"]
            
            # Optimize et
            optimized_text, usage = await self.llm_client.optimize_prompt(original_prompt)
            
            # LIME analizi yap
            lime_analysis = await self.lime_analyzer.analyze_prompt(original_prompt, optimized_text)
            
            # Yanıtı kaydet
            response_data = {
                "iteration": len(prompt_data["model_responses"]) + 1,
                "prompt_text": original_prompt,
                "optimized_text": optimized_text,
                "model_name": "gpt-3.5-turbo",
                **usage,
                "timestamp": datetime.utcnow().isoformat(),
                "lime_analysis": lime_analysis
            }
            
            await self.db.add_model_response(prompt_id, response_data)
            await self.db.update_prompt(prompt_id, {
                "optimized_prompt": optimized_text,
                "lime_analysis": lime_analysis
            })
            
            logger.info(f"Prompt optimize edildi", extra={
                "prompt_id": str(prompt_id),
                "tokens": usage["total_tokens"],
                "confidence_score": lime_analysis["confidence_score"]
            })
            
            # Veritabanından sonucu al ve eksik alanları doldur
            result = await self.db.get_prompt(prompt_id)
            if result:
                result["prompt_id"] = str(result.pop("_id"))
                # Eksik model_name alanlarını doldur
                for response in result.get("model_responses", []):
                    if "model_name" not in response:
                        response["model_name"] = "gpt-3.5-turbo"
                    if "lime_analysis" not in response:
                        response["lime_analysis"] = None
            return result
            
        except Exception as e:
            logger.error(f"Prompt optimizasyon hatası: {str(e)}")
            raise
            
    async def get_metrics(self, prompt_id: str) -> Dict:
        """Prompt metrikleri getir"""
        try:
            metrics = await self.db.get_prompt_metrics(prompt_id)
            return metrics
        except Exception as e:
            logger.error(f"Metrik getirme hatası: {str(e)}")
            raise 
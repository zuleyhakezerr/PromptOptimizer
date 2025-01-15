from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List
from pydantic import BaseModel, Field
from datetime import datetime

from ...services.prompt_service import PromptService
from ...config.settings import get_settings
from ...utils.logger import logger

router = APIRouter()
settings = get_settings()

class PromptRequest(BaseModel):
    text: str
    model_name: str = "gpt-3.5-turbo"
    temperature: float = 0.7

class LIMEAnalysis(BaseModel):
    token_importance: Dict[str, float]
    changes: List[Dict]
    explanation: str
    confidence_score: float

class ModelResponse(BaseModel):
    iteration: int
    prompt_text: str
    model_name: str
    completion_text: str | None = None
    optimized_text: str | None = None
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float
    timestamp: str
    lime_analysis: LIMEAnalysis | None = None

class PromptResponse(BaseModel):
    prompt_id: str
    original_prompt: str
    model_responses: List[ModelResponse]
    status: str
    created_at: str
    optimized_prompt: str | None = None
    lime_analysis: LIMEAnalysis | None = None

class MetricsResponse(BaseModel):
    prompt_id: str
    total_tokens: int
    total_cost_usd: float
    iterations: int
    original_prompt_length: int
    optimized_prompt_length: int | None = None

def format_response(data: Dict) -> Dict:
    """API response modellerine uygun formatta veriyi düzenle"""
    if not data:
        return data
        
    # Model yanıtlarını düzenle
    if "model_responses" in data:
        for response in data["model_responses"]:
            if "optimized_text" in response:
                response["completion_text"] = response.pop("optimized_text")
            if "lime_analysis" not in response:
                response["lime_analysis"] = None
                
    return data

@router.post("/prompt", response_model=PromptResponse)
async def create_prompt(prompt: PromptRequest) -> Dict:
    """Yeni bir prompt oluştur"""
    try:
        service = PromptService()
        result = await service.create_prompt(
            text=prompt.text,
            model_name=prompt.model_name,
            temperature=prompt.temperature
        )
        return format_response(result)
    except Exception as e:
        logger.error(f"Prompt oluşturma hatası: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize/{prompt_id}", response_model=PromptResponse)
async def optimize_prompt(prompt_id: str) -> Dict:
    """Var olan promptu optimize et"""
    try:
        service = PromptService()
        result = await service.optimize_prompt(prompt_id)
        return format_response(result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Prompt optimizasyon hatası: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/{prompt_id}", response_model=MetricsResponse)
async def get_metrics(prompt_id: str) -> Dict:
    """Prompt metrikleri getir"""
    try:
        service = PromptService()
        result = await service.get_metrics(prompt_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"Prompt bulunamadı: {prompt_id}")
        return result
    except Exception as e:
        logger.error(f"Metrik getirme hatası: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 
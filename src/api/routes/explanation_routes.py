from fastapi import APIRouter, HTTPException
from typing import Dict, List
from pydantic import BaseModel

router = APIRouter()

class TokenAnalysis(BaseModel):
    token_importance: Dict[str, float]
    changes: List[Dict[str, str]]
    explanation: str
    confidence_score: float

@router.get("/analyze/{prompt_id}")
async def get_token_analysis(prompt_id: str) -> TokenAnalysis:
    try:
        # LIME analizi ve token önem skorları hesaplama
        # Bu kısım LIME servisine bağlanacak
        return TokenAnalysis(
            token_importance={"token1": 0.8, "token2": 0.6},
            changes=[
                {
                    "position": 1,
                    "original": "eski",
                    "optimized": "yeni",
                    "type": "replacement"
                }
            ],
            explanation="Token analizi açıklaması",
            confidence_score=0.85
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
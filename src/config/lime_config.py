from pydantic_settings import BaseSettings
from functools import lru_cache

class LIMESettings(BaseSettings):
    # LIME parametreleri
    num_samples: int = 1000
    kernel_width: float = 0.25
    feature_selection: str = "auto"
    
    # Token analiz parametreleri
    importance_threshold: float = 0.1
    min_token_length: int = 2
    
    # Görselleştirme ayarları
    color_scheme: str = "viridis"
    interactive: bool = True
    export_formats: list = ["html", "png", "pdf"]
    
    # Karşılaştırma metrikleri
    comparison_metrics: list = [
        "semantic_similarity",
        "token_efficiency",
        "context_preservation"
    ]
    
    # Görselleştirme tipleri
    visualization_types: list = [
        "side_by_side",
        "diff_highlight",
        "impact_scores"
    ]
    
    class Config:
        case_sensitive = True

@lru_cache()
def get_lime_settings() -> LIMESettings:
    """LIME ayarlarını önbellekle ve döndür"""
    return LIMESettings() 
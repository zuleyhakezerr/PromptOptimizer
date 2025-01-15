from typing import Dict, List, Tuple
import numpy as np
from lime.lime_text import LimeTextExplainer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import plotly.graph_objects as go
import plotly.express as px
from ..utils.text_processing import tokenize_text, preprocess_text
from ..config.lime_config import get_lime_settings

class LIMEAnalyzer:
    def __init__(self):
        self.settings = get_lime_settings()
        self.explainer = LimeTextExplainer(
            kernel_width=self.settings.kernel_width,
            class_names=['original', 'optimized'],
            bow=False
        )
        self.vectorizer = TfidfVectorizer(
            tokenizer=tokenize_text,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
    async def analyze_prompt(self, original_prompt: str, optimized_prompt: str) -> Dict:
        """Prompt optimizasyonunu LIME ile analiz et"""
        try:
            # Metinleri hazırla
            original_tokens = tokenize_text(original_prompt)
            optimized_tokens = tokenize_text(optimized_prompt)
            
            # LIME açıklaması oluştur
            exp = self.explainer.explain_instance(
                original_prompt,
                self._prediction_fn,
                num_features=len(original_tokens),
                num_samples=self.settings.num_samples,
                top_labels=1
            )
            
            # Token önem skorlarını hesapla
            token_importance = self._calculate_token_importance(exp)
            
            # Değişiklikleri analiz et
            changes = self._analyze_changes(original_tokens, optimized_tokens)
            
            # Görselleştirmeleri oluştur
            visualizations = self._create_visualizations(
                token_importance,
                changes,
                original_prompt,
                optimized_prompt
            )
            
            return {
                "token_importance": token_importance,
                "changes": changes,
                "explanation": self._format_explanation(exp, changes),
                "confidence_score": self._calculate_confidence(exp),
                "visualizations": visualizations,
                "metrics": self._calculate_metrics(original_prompt, optimized_prompt)
            }
            
        except Exception as e:
            raise Exception(f"LIME analizi sırasında hata: {str(e)}")
        
    def _prediction_fn(self, texts: List[str]) -> np.ndarray:
        """LIME için gelişmiş tahmin fonksiyonu"""
        predictions = []
        for text in texts:
            # TF-IDF vektörleştirme
            features = self.vectorizer.fit_transform([text]).toarray()
            
            # Metrikleri hesapla
            length_score = 1.0 - (len(text.split()) / 100)  # Uzunluk skoru
            complexity_score = self._calculate_complexity_score(text)
            clarity_score = self._calculate_clarity_score(text)
            
            # Skorları birleştir
            final_score = (length_score + complexity_score + clarity_score) / 3
            predictions.append([1 - final_score, final_score])
            
        return np.array(predictions)
        
    def _calculate_complexity_score(self, text: str) -> float:
        """Metin karmaşıklığını hesapla"""
        words = text.split()
        avg_word_length = sum(len(word) for word in words) / len(words)
        return 1.0 - (avg_word_length / 10)  # 10 karakterden uzun kelimeler cezalandırılır
        
    def _calculate_clarity_score(self, text: str) -> float:
        """Metin netliğini hesapla"""
        sentences = text.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        return 1.0 - (avg_sentence_length / 20)  # 20 kelimeden uzun cümleler cezalandırılır
        
    def _create_visualizations(
        self,
        token_importance: Dict[str, float],
        changes: List[Dict],
        original_prompt: str,
        optimized_prompt: str
    ) -> Dict:
        """Görselleştirmeler oluştur"""
        return {
            "token_heatmap": self._create_token_heatmap(token_importance),
            "changes_sankey": self._create_changes_sankey(changes),
            "metrics_radar": self._create_metrics_radar(original_prompt, optimized_prompt),
            "importance_distribution": self._create_importance_distribution(token_importance)
        }
        
    def _create_token_heatmap(self, token_importance: Dict[str, float]) -> Dict:
        """Token önem skorları ısı haritası"""
        tokens = list(token_importance.keys())
        scores = list(token_importance.values())
        
        fig = go.Figure(data=go.Heatmap(
            z=[scores],
            x=tokens,
            colorscale='RdYlBu',
            showscale=True
        ))
        
        fig.update_layout(
            title="Token Önem Skorları Isı Haritası",
            xaxis_title="Tokenlar",
            yaxis_title="Önem Skoru",
            height=200
        )
        
        return fig.to_dict()
        
    def _create_changes_sankey(self, changes: List[Dict]) -> Dict:
        """Değişiklikler için Sankey diyagramı"""
        source = []
        target = []
        value = []
        
        for change in changes:
            source.append(change['original'])
            target.append(change['optimized'])
            value.append(1)
            
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=list(set(source + target))
            ),
            link=dict(
                source=source,
                target=target,
                value=value
            )
        )])
        
        fig.update_layout(
            title="Token Değişiklikleri Akış Diyagramı",
            height=400
        )
        
        return fig.to_dict()
        
    def _create_metrics_radar(self, original_prompt: str, optimized_prompt: str) -> Dict:
        """Metrikler için radar grafik"""
        metrics = self._calculate_metrics(original_prompt, optimized_prompt)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=[metrics[key] for key in metrics.keys()],
            theta=list(metrics.keys()),
            fill='toself',
            name='Optimizasyon Metrikleri'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            showlegend=True,
            title="Optimizasyon Metrikleri Radar Grafiği"
        )
        
        return fig.to_dict()
        
    def _create_importance_distribution(self, token_importance: Dict[str, float]) -> Dict:
        """Token önem dağılımı histogramı"""
        scores = list(token_importance.values())
        
        fig = go.Figure(data=[go.Histogram(
            x=scores,
            nbinsx=20,
            name="Önem Skorları"
        )])
        
        fig.update_layout(
            title="Token Önem Skorları Dağılımı",
            xaxis_title="Önem Skoru",
            yaxis_title="Token Sayısı",
            height=300
        )
        
        return fig.to_dict()
        
    def _calculate_metrics(self, original_prompt: str, optimized_prompt: str) -> Dict:
        """Detaylı metrikler hesapla"""
        try:
            return {
                "token_reduction": self._calculate_token_reduction(original_prompt, optimized_prompt),
                "clarity_improvement": self._calculate_clarity_score(optimized_prompt) - self._calculate_clarity_score(original_prompt),
                "complexity_reduction": self._calculate_complexity_score(optimized_prompt) - self._calculate_complexity_score(original_prompt),
                "semantic_preservation": self._calculate_semantic_similarity(original_prompt, optimized_prompt),
                "optimization_confidence": 0.8  # Sabit bir değer kullanıyoruz
            }
        except Exception as e:
            # Hata durumunda varsayılan değerler döndür
            return {
                "token_reduction": 0.0,
                "clarity_improvement": 0.0,
                "complexity_reduction": 0.0,
                "semantic_preservation": 1.0,
                "optimization_confidence": 0.5
            }
        
    def _calculate_token_reduction(self, original: str, optimized: str) -> float:
        """Token azaltma oranı"""
        original_tokens = len(tokenize_text(original))
        optimized_tokens = len(tokenize_text(optimized))
        return 1.0 - (optimized_tokens / original_tokens)
        
    def _calculate_semantic_similarity(self, original: str, optimized: str) -> float:
        """Anlamsal benzerlik skoru"""
        # TF-IDF vektörleri ile kosinüs benzerliği
        vectors = self.vectorizer.fit_transform([original, optimized])
        similarity = (vectors * vectors.T).toarray()[0, 1]
        return float(similarity)
        
    def _calculate_optimization_confidence(self, original: str, optimized: str) -> float:
        """Optimizasyon güven skoru"""
        metrics = self._calculate_metrics(original, optimized)
        return sum(metrics.values()) / len(metrics)
        
    def _calculate_token_importance(self, explanation) -> Dict[str, float]:
        """Token bazında önem skorlarını hesapla"""
        importance_dict = {}
        for token, score in explanation.as_list():
            if abs(score) > self.settings.importance_threshold:
                importance_dict[token] = float(score)
        return importance_dict
        
    def _analyze_changes(self, original_tokens: List[str], optimized_tokens: List[str]) -> List[Dict]:
        """Yapılan değişiklikleri analiz et"""
        changes = []
        for i, (orig, opt) in enumerate(zip(original_tokens, optimized_tokens)):
            if orig != opt:
                changes.append({
                    "position": i,
                    "original": orig,
                    "optimized": opt,
                    "type": "replacement"
                })
        return changes
        
    def _format_explanation(self, explanation, changes: List[Dict]) -> str:
        """İnsan tarafından okunabilir açıklama oluştur"""
        exp_text = "Optimizasyon Açıklaması:\n\n"
        
        # Önemli değişiklikleri açıkla
        for change in changes:
            exp_text += f"- '{change['original']}' yerine '{change['optimized']}' kullanıldı "
            exp_text += f"(pozisyon: {change['position']})\n"
            
        # Genel önerileri ekle
        exp_text += "\nGenel Öneriler:\n"
        for token, score in explanation.as_list()[:5]:  # En önemli 5 değişiklik
            if score > 0:
                exp_text += f"- '{token}' kelimesi/ifadesi korunmalı (skor: {score:.2f})\n"
            else:
                exp_text += f"- '{token}' kelimesi/ifadesi değiştirilmeli (skor: {score:.2f})\n"
                
        return exp_text
        
    def _calculate_confidence(self, explanation) -> float:
        """Optimizasyon güven skorunu hesapla"""
        scores = [abs(score) for _, score in explanation.as_list()]
        return float(np.mean(scores)) 
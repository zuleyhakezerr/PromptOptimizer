from typing import List
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# NLTK gerekli dosyaları indir
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

def tokenize_text(text: str) -> List[str]:
    """Metni tokenlara ayır"""
    return word_tokenize(text)

def preprocess_text(text: str) -> str:
    """Metni ön işlemden geçir"""
    # Küçük harfe çevir
    text = text.lower()
    
    # Gereksiz boşlukları temizle
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Noktalama işaretlerini kaldır
    text = re.sub(r'[^\w\s]', '', text)
    
    return text

def remove_stopwords(tokens: List[str], language: str = 'english') -> List[str]:
    """Stop word'leri kaldır"""
    stop_words = set(stopwords.words(language))
    return [token for token in tokens if token.lower() not in stop_words]

def calculate_similarity(text1: str, text2: str) -> float:
    """İki metin arasındaki benzerliği hesapla"""
    # Metinleri tokenize et
    tokens1 = set(tokenize_text(preprocess_text(text1)))
    tokens2 = set(tokenize_text(preprocess_text(text2)))
    
    # Jaccard benzerliği hesapla
    intersection = len(tokens1.intersection(tokens2))
    union = len(tokens1.union(tokens2))
    
    return intersection / union if union > 0 else 0.0

def extract_key_phrases(text: str, top_n: int = 5) -> List[str]:
    """Metinden anahtar ifadeleri çıkar"""
    # Metni tokenize et ve stop word'leri kaldır
    tokens = tokenize_text(preprocess_text(text))
    tokens = remove_stopwords(tokens)
    
    # Basit frekans bazlı anahtar kelime çıkarımı
    freq_dist = nltk.FreqDist(tokens)
    return [word for word, _ in freq_dist.most_common(top_n)]

def analyze_prompt_structure(prompt: str) -> dict:
    """Prompt yapısını analiz et"""
    tokens = tokenize_text(prompt)
    words = [token for token in tokens if token.isalnum()]
    
    return {
        "total_length": len(prompt),
        "word_count": len(words),
        "avg_word_length": sum(len(word) for word in words) / len(words) if words else 0,
        "key_phrases": extract_key_phrases(prompt),
        "has_question_mark": "?" in prompt,
        "sentence_count": len(nltk.sent_tokenize(prompt))
    }

def highlight_differences(original: str, optimized: str) -> dict:
    """İki metin arasındaki farkları vurgula"""
    # Metinleri tokenize et
    original_tokens = tokenize_text(original)
    optimized_tokens = tokenize_text(optimized)
    
    # Değişiklikleri bul
    changes = []
    for i, (orig, opt) in enumerate(zip(original_tokens, optimized_tokens)):
        if orig != opt:
            changes.append({
                "position": i,
                "original": orig,
                "optimized": opt,
                "type": "replacement"
            })
    
    # Silinen ve eklenen tokenleri bul
    if len(original_tokens) > len(optimized_tokens):
        for i in range(len(optimized_tokens), len(original_tokens)):
            changes.append({
                "position": i,
                "original": original_tokens[i],
                "optimized": None,
                "type": "deletion"
            })
    elif len(optimized_tokens) > len(original_tokens):
        for i in range(len(original_tokens), len(optimized_tokens)):
            changes.append({
                "position": i,
                "original": None,
                "optimized": optimized_tokens[i],
                "type": "addition"
            })
    
    return {
        "changes": changes,
        "similarity_score": calculate_similarity(original, optimized),
        "change_count": len(changes)
    } 
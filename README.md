# Prompt Optimizer

Bu proje, kullanıcılardan gelen ham promptları optimize eden, LLM çıktılarını analiz eden ve token/maliyet metriklerini hesaplayan bir sistemdir.

## Özellikler

- Ham promptları otomatik optimize etme
- GPT-3.5/GPT-4 model entegrasyonu
- Token kullanımı ve maliyet analizi
- Detaylı metrik raporlama
- LIME analizi ile token önem skorları
- MongoDB ile veri saklama
- Vue.js tabanlı modern arayüz

## Kurulum

### Backend Kurulumu

1. Python 3.12 veya üstü gereklidir.

2. Sanal ortam oluşturun ve aktifleştirin:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
.\venv\Scripts\activate  # Windows
```

3. Gereksinimleri yükleyin:
```bash
pip install -r requirements.txt
```

4. MongoDB'yi kurun ve başlatın:
```bash
# MongoDB'yi yerel olarak çalıştırın veya MongoDB Atlas kullanın
```

5. `.env` dosyasını oluşturun:
```bash
cp .env.example .env
```

6. `.env` dosyasını düzenleyin:
```
OPENAI_API_KEY=your_api_key_here
MONGODB_URI=mongodb://localhost:27017
PORT=8000
DEBUG=true
```

### Frontend Kurulumu

1. Node.js 18 veya üstü gereklidir.

2. Frontend dizinine gidin:
```bash
cd frontend
```

3. Bağımlılıkları yükleyin:
```bash
npm install
```

## Çalıştırma

### Backend'i Başlatma

1. Ana dizinde:
```bash
uvicorn src.api.main:app --reload --port 8000
```

2. API şu adreste çalışacak: http://localhost:8000
   - API Dokümantasyonu: http://localhost:8000/docs
   - Ana Sayfa: http://localhost:8000

### Frontend'i Başlatma

1. Frontend dizininde:
```bash
cd frontend
npm run dev
```

2. Frontend şu adreste çalışacak: http://localhost:5173

## API Endpoint'leri

- `POST /api/v1/prompts/prompt`: Yeni prompt oluştur
- `POST /api/v1/prompts/optimize/{prompt_id}`: Promptu optimize et
- `GET /api/v1/prompts/metrics/{prompt_id}`: Prompt metriklerini getir

## Geliştirme

- Testleri çalıştırma: `pytest`
- Kod formatı: `black src/`
- Lint kontrolü: `flake8 src/`

## Lisans

MIT 
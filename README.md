# Destek Admin - Sesli ve Yazılı Konuşma Sistemi

Minimal, mobil-first chat + WebRTC sesli/görüntülü arama uygulaması.

## 🚀 Hızlı Başlangıç

### Lokal Çalıştırma

```bash
# 1) Sanal ortam oluştur
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2) Bağımlılıkları yükle
pip install -r requirements.txt

# 3) Çalıştır
python -m server.app
```

Tarayıcıda aç: http://localhost:10000/

### Ortam Değişkenleri

`.env` dosyası oluştur (`.env.example`'dan kopyala):

```env
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
TZ=Europe/Istanbul
DATABASE_URL=sqlite:///./data.sqlite3

# CORS
ALLOWED_ORIGINS=http://localhost:10000

# Telegram (opsiyonel)
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ADMIN_CHAT_ID=your-chat-id
TELEGRAM_WEBHOOK_URL=https://your-app.onrender.com/tg/webhook
```

## 📦 Render.com Deploy

### 1. GitHub'a Push

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/mhzn1031-ai/destekadmin.git
git push -u origin main
```

### 2. Render'da Yeni Web Service

1. [Render Dashboard](https://dashboard.render.com/) → **New** → **Web Service**
2. GitHub repo'nuzu bağlayın: `mhzn1031-ai/destekadmin`
3. Ayarlar:
   - **Name**: `destekadmin`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m server.app`
   - **Plan**: Free

### 3. Environment Variables Ekle

Render dashboard'da **Environment** sekmesinden:

```
FLASK_ENV=production
SECRET_KEY=<generate-random-key>
TZ=Europe/Istanbul
ALLOWED_ORIGINS=https://destekadmin.onrender.com
```

Telegram kullanacaksanız:
```
TELEGRAM_BOT_TOKEN=<your-token>
TELEGRAM_ADMIN_CHAT_ID=<your-chat-id>
TELEGRAM_WEBHOOK_URL=https://destekadmin.onrender.com/tg/webhook
```

### 4. Deploy

**Create Web Service** butonuna tıklayın. Deploy otomatik başlar.

## 🎯 Özellikler

- ✅ Mobil-first tasarım
- ✅ Tam ekran chat
- ✅ WebRTC P2P sesli/görüntülü arama
- ✅ Telegram entegrasyonu
- ✅ Admin paneli
- ✅ Test & Repair araçları
- ✅ SQLite veritabanı
- ✅ Zamanlanmış testler

## 📱 Kullanım

### Müşteri (/)
1. İsim gir
2. Chat ekranı açılır
3. Sağ üstteki 📞 ile arama başlat

### Admin (/admin)
1. OTP ile giriş (demo)
2. Bekleyen sohbetleri gör
3. Chat yap veya ara

### Test (/test)
1. Sistem testlerini çalıştır
2. Zamanlanmış test saatleri ekle
3. Repair işlemleri

## 🔧 Teknoloji

- **Backend**: Flask + Flask-SocketIO (eventlet)
- **Database**: SQLite + SQLAlchemy
- **Frontend**: Vanilla HTML/CSS/JS
- **WebRTC**: P2P audio/video
- **Scheduler**: APScheduler

## 📄 Lisans

MIT

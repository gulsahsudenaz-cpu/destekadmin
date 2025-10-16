# 📞 Destek Admin - Profesyonel Müşteri Destek Sistemi

> Modern, mobil-first chat + WebRTC sesli/görüntülü arama platformu

[![Live Demo](https://img.shields.io/badge/🌐_Live_Demo-destekadmin.onrender.com-blue?style=for-the-badge)](https://destekadmin.onrender.com/)
[![GitHub](https://img.shields.io/badge/📂_GitHub-Repository-black?style=for-the-badge)](https://github.com/gulsahsudenaz-cpu/destekadmin)
[![Python](https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge&logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1+-green?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com/)

## 🌟 Canlı Demo

**🔗 Ana Site:** https://destekadmin.onrender.com/  
**👨‍💼 Admin Panel:** https://destekadmin.onrender.com/admin  
**🧪 Test Paneli:** https://destekadmin.onrender.com/test  
**❤️ Health Check:** https://destekadmin.onrender.com/health

## 🚀 Hızlı Başlangıç

### 📱 Canlı Demo'yu Deneyin

1. **Müşteri Deneyimi:** [destekadmin.onrender.com](https://destekadmin.onrender.com/)
   - İsminizi girin ve chat'e başlayın
   - Sağ üstteki 📞 butonuyla sesli arama başlatın

2. **Admin Paneli:** [destekadmin.onrender.com/admin](https://destekadmin.onrender.com/admin)
   - OTP: `demo` (test için)
   - Bekleyen sohbetleri görün ve yanıtlayın

### 💻 Lokal Kurulum

```bash
# Repository'yi klonlayın
git clone https://github.com/gulsahsudenaz-cpu/destekadmin.git
cd destekadmin

# Sanal ortam oluşturun
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Bağımlılıkları yükleyin
pip install -r requirements.txt

# Uygulamayı başlatın
python -m server.app
```

🌐 **Tarayıcıda açın:** http://localhost:10000/

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

## 🚀 Deploy (Render.com)

### 1. Fork & Clone

```bash
# Bu repository'yi fork edin, sonra:
git clone https://github.com/YOUR_USERNAME/destekadmin.git
cd destekadmin

# Değişikliklerinizi yapın ve push edin
git add .
git commit -m "My customizations"
git push origin main
```

### 2. Render'da Deploy

1. **[Render Dashboard](https://dashboard.render.com/)** → **New** → **Web Service**
2. **GitHub repo'nuzu bağlayın:** `YOUR_USERNAME/destekadmin`
3. **Ayarlar:**
   ```
   Name: destekadmin
   Environment: Python 3
   Build Command: pip install --upgrade pip && pip install -r requirements.txt
   Start Command: python -m server.app
   Plan: Free
   ```

### 3. Environment Variables

**Render Dashboard** → **Environment** sekmesinde ekleyin:

```env
# Zorunlu
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here
TZ=Europe/Istanbul
ALLOWED_ORIGINS=https://YOUR-APP-NAME.onrender.com

# Performans
WEB_CONCURRENCY=1
MAX_WORKERS=1
WORKER_TIMEOUT=120

# Güvenlik
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax

# Telegram (opsiyonel)
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ADMIN_CHAT_ID=your-chat-id
TELEGRAM_WEBHOOK_URL=https://YOUR-APP-NAME.onrender.com/tg/webhook
```

> 🔑 **SECRET_KEY oluşturmak için:** `python -c "import secrets; print(secrets.token_urlsafe(32))"`

### 4. Deploy

**Create Web Service** butonuna tıklayın. Deploy otomatik başlar.

## ✨ Özellikler

### 📱 Kullanıcı Deneyimi
- 🎆 **Modern UI/UX** - Mobil-first, responsive tasarım
- 💬 **Anlık Mesajlaşma** - Socket.IO ile gerçek zamanlı
- 📞 **Sesli/Görüntülü Arama** - WebRTC P2P teknolojisi
- 🖼️ **Medya Paylaşımı** - Resim ve ses dosyaları
- 🌍 **Cross-Platform** - Tüm cihazlarda çalışır

### 👨‍💼 Admin Yönetimi
- 🔐 **Güvenli Giriş** - OTP tabanlı kimlik doğrulama
- 📈 **Chat Yönetimi** - Sohbet geçmişi ve analiz
- 🤖 **Telegram Entegrasyonu** - Bot bildirimleri
- 🧪 **Test Sistemi** - Otomatik sağlık kontrolleri
- 🔧 **Bakım Araçları** - Sistem temizleme ve onarım

### 🔒 Güvenlik & Performans
- 🛡️ **Rate Limiting** - API koruması
- 🌐 **CORS & CSP** - Cross-origin güvenliği
- 🔍 **XSS Koruması** - Input sanitization
- 📉 **Professional Logging** - Detaylı sistem logları
- ❤️ **Health Monitoring** - Canlılık kontrolü
- 🚀 **Production Ready** - Render.com deploy desteği

## 📱 Kullanım Kılavuzu

### 👥 Müşteri Paneli (`/`)

1. **📝 İsim Girişi**
   - Adınızı girin (max 30 karakter)
   - "Chat'e Başla" butonuna tıklayın

2. **💬 Mesajlaşma**
   - Alt kısımdaki input alanına mesajınızı yazın
   - Enter tuşu veya "Gönder" butonu ile gönderin
   - 🖼️ Resim, 🎤 Ses dosyası paylaşabilirsiniz

3. **📞 Sesli/Görüntülü Arama**
   - Sağ üstteki yeşil telefon ikonuna tıklayın
   - Mikrofon erişimine izin verin
   - Admin yanıtlayınca arama başlar

### 👨💼 Admin Paneli (`/admin`)

1. **🔐 Güvenli Giriş**
   - OTP: `demo` (test ortamı için)
   - Üretim ortamında güvenli OTP kullanın

2. **📈 Sohbet Yönetimi**
   - Sol panelde bekleyen sohbetleri görün
   - Sohbete tıklayarak mesaj geçmişini açın
   - 📞 Arama başlat veya 🗑️ Sil butonlarını kullanın

3. **💬 Yanıtlama**
   - Alt kısımdaki input'a yanıtınızı yazın
   - Enter veya "Gönder" ile gönderin

### 🧪 Test Paneli (`/test`)

1. **🔍 Sistem Testleri**
   - "Test Çalıştır" butonu ile anlık test
   - Sağlık durumu, veritabanı, API kontrolleri

2. **⏰ Zamanlanmış Testler**
   - Otomatik test saatleri ekleyin (HH:MM formatı)
   - Enable/disable ile aktif/pasif yapın

3. **🔧 Sistem Bakımı**
   - "Repair Çalıştır" ile sistem temizliği
   - Eski chat'leri ve logları temizler

## 🔧 Teknoloji Stack

### 🔙 Backend
- **🐍 Python 3.12+** - Modern Python
- **🌶️ Flask 3.1.0** - Lightweight web framework
- **🔌 Flask-SocketIO 5.4.1** - Real-time communication
- **⚡ Eventlet 0.36.1** - Async networking
- **🗄 SQLAlchemy 2.0.36** - Database ORM
- **⏰ APScheduler 3.10.4** - Task scheduling

### 🌐 Frontend
- **🎨 Modern CSS** - Custom properties, Grid, Flexbox
- **📱 Mobile-First** - Responsive design
- **⚡ Vanilla JavaScript** - No framework dependencies
- **📞 WebRTC** - P2P audio/video calls
- **🔌 Socket.IO Client** - Real-time updates

### 📦 Database & Storage
- **🗄 SQLite** - Embedded database
- **📁 File Storage** - Media uploads
- **📋 Session Management** - User state

### 🚀 Deployment
- **🌐 Render.com** - Cloud hosting
- **🐳 Docker** - Containerization
- **🔐 Environment Variables** - Configuration
- **📈 Health Monitoring** - Uptime tracking

### 🔒 Güvenlik
- **🛡️ Rate Limiting** - API protection
- **🌐 CORS** - Cross-origin security
- **📜 CSP** - Content Security Policy
- **🔍 Input Sanitization** - XSS prevention

---

## 📄 Lisans

**MIT License** - Özgürce kullanılabilir, değiştirilebilir ve dağıtılabilir.

## 👥 Katkıda Bulunun

1. **Fork** edin
2. **Feature branch** oluşturun (`git checkout -b feature/amazing-feature`)
3. **Commit** edin (`git commit -m 'Add amazing feature'`)
4. **Push** edin (`git push origin feature/amazing-feature`)
5. **Pull Request** açın

## 🐛 Sorun Bildirimi

Sorun mu buldunuz? [GitHub Issues](https://github.com/gulsahsudenaz-cpu/destekadmin/issues) sayfasından bildirebilirsiniz.

## 📧 İletişim

Sorularınız için GitHub Issues kullanın veya repository'yi star'layıp takip edin!

---

<div align="center">

**⭐ Beğendiyseniz star vermeyi unutmayın!**

[![GitHub stars](https://img.shields.io/github/stars/gulsahsudenaz-cpu/destekadmin?style=social)](https://github.com/gulsahsudenaz-cpu/destekadmin/stargazers)

</div>

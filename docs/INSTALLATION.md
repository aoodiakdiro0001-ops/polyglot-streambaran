# 📦 دليل التثبيت — PolyGlot-StreamBaran

**المؤلف:** Baran Avisat | **البريد:** Baranavisat@gmail.com | **واتساب:** 00905313263722

---

## المتطلبات المسبقة

### 1. تثبيت Python 3.10+
```bash
# أوبونتو/ديبيان
sudo apt update && sudo apt install python3.11 python3-pip

# ويندوز (حمّل من python.org)
# تأكد من تفعيل "Add Python to PATH"

# macOS
brew install python@3.11
```

### 2. تثبيت ffmpeg
```bash
# أوبونتو
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# ويندوز: حمّل من ffmpeg.org وأضفه إلى PATH
```

### 3. تثبيت Git
```bash
sudo apt install git   # Linux
brew install git       # macOS
```

---

## خطوات التثبيت

### الخطوة 1: استنساخ المشروع
```bash
git clone <repo-url>
cd PolyGlot-StreamBaran
```

### الخطوة 2: إنشاء بيئة افتراضية
```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
```

### الخطوة 3: تثبيت المتطلبات
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### الخطوة 4: الحصول على المفاتيح المجانية

| الخدمة | الرابط | المدة |
|---|---|---|
| Hugging Face Token | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) | 2 دقيقة |
| Google Gemini API | [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) | 2 دقيقة |
| Groq API (بديل) | [console.groq.com/keys](https://console.groq.com/keys) | 2 دقيقة |
| Supabase | [supabase.com](https://supabase.com) | 5 دقائق |
| Telegram Bot | [@BotFather](https://t.me/BotFather) | 3 دقائق |

### الخطوة 5: إعداد ملف .env
```bash
cp .env.example .env
nano .env   # أو استخدم أي محرر
```

أضف مفاتيحك:
```env
GEMINI_API_KEY=AIza...
HF_TOKEN=hf_...
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=eyJ...
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
TELEGRAM_CHAT_ID=123456789
```

### الخطوة 6: تهيئة قاعدة بيانات Supabase

1. ادخل لوحة تحكم Supabase → SQL Editor
2. انسخ محتوى `SQL_SCHEMA` من ملف `src/database.py`
3. الصقه في SQL Editor واضغط **Run**

### الخطوة 7: الحصول على Telegram Chat ID
```bash
# أرسل رسالة لبوتك ثم افتح:
https://api.telegram.org/bot<TOKEN>/getUpdates
# ابحث عن "chat":{"id":XXXXX
```

---

## التشغيل

### تشغيل بوت تليجرام
```bash
python -m telegram_bot.bot
```

### تشغيل واجهة الويب
```bash
cd web_dashboard
streamlit run app.py
# ستفتح على http://localhost:8501
```

### تشغيل من CLI
```bash
python main.py --url "https://youtube.com/watch?v=XXXX" --lang ar
python main.py --file audio.mp3 --lang en --provider groq
```

---

## التحقق من التثبيت

```bash
python -c "from config import CONFIG; print(CONFIG.AUTHOR_NAME)"
# يجب أن يطبع: Baran Avisat

python -m pytest tests/ -v
# يجب أن تنجح كل الاختبارات
```

---

## النشر على Hugging Face Spaces

1. أنشئ Space جديد على [huggingface.co/new-space](https://huggingface.co/new-space)
2. اختر SDK: **Streamlit** أو **Gradio**
3. ارفع محتوى مجلد `huggingface_space/`
4. أضف المفاتيح في **Settings > Repository secrets**
5. سيعمل التطبيق على `https://<user>-polyglot-streambaran.hf.space`

---

## النشر على GitHub Actions

1. ارفع المشروع إلى GitHub
2. في إعدادات المستودع → **Secrets and variables > Actions**
3. أضف كل المفاتيح كـ Secrets
4. عدّل `github_actions/workflow.yml` حسب احتياجك
5. شغّل الـ workflow يدوياً أو دعه يعمل مجدولاً

---

## استكشاف الأخطاء

### خطأ: `ModuleNotFoundError: No module named 'whisper'`
```bash
pip install openai-whisper
```

### خطأ: `ffmpeg not found`
```bash
sudo apt install ffmpeg  # Linux
```

### خطأ: `Supabase connection refused`
- تحقق من SUPABASE_URL و SUPABASE_KEY
- تأكد من تنفيذ SQL_SCHEMA

### خطأ: `Telegram Unauthorized`
- تحقق من TELEGRAM_BOT_TOKEN
- أنشئ بوتاً جديداً من @BotFather

---

**© 2026 Baran Avisat. للدعم: Baranavisat@gmail.com**

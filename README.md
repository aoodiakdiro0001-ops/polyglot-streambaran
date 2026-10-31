# 🌐 PolyGlot-StreamBaran

<div align="center">

**المنظومة الذاتية للترجمة، تفريغ الصوت، وتوليد الترجمات المرئية**

![Version](https://img.shields.io/badge/version-1.0.0-indigo)
![License](https://img.shields.io/badge/license-Proprietary-red)
![Python](https://img.shields.io/badge/python-3.10+-green)
![Free](https://img.shields.io/badge/cost-100%25%20FREE-success)

**نظام ذكي متكامل ومستقل لتحويل التسجيلات الصوتية ومقاطع الفيديو إلى نصوص دقيقة، تفريغ المحتوى مع التوقيت الزمني (SRT)، ترجمته فوراً إلى أي لغة، وتوليد ملخصات تنفيذية للمحتوى — بتكلفة صفر وبموارد مجانية بالكامل.**

</div>

---

## 👤 المؤلف وحقوق الملكية

| الحقل | القيمة |
|---|---|
| **المؤلف** | Baran Avisat |
| **البريد الإلكتروني** | Baranavisat@gmail.com |
| **رقم الواتساب** | 00905313263722 |
| **الإصدار** | 1.0.0 |
| **الترخيص** | Proprietary — جميع الحقوق محفوظة (التجاري بإذن خطى) |

> © 2026 Baran Avisat. جميع الحقوق محفوظة. الاستخدام التجاري يتطلب إذناً خطياً من المالك.

---

## 📖 نظرة عامة

**PolyGlot-StreamBaran** هو نظام ذكي متكامل ومستقل يقوم بـ:

1. **استلام** روابط الفيديو أو الملفات الصوتية عبر تليجرام أو واجهة الويب.
2. **استخراج الكلام** عبر نموذج Whisper مفتوح المصدر (جودة الاستخراج تعتمد على وضوح المدخلات الصوتية).
3. **الترجمة الفورية** دلالياً إلى أكثر من 12 لغة عبر Gemini/Groq API.
4. **توليد ملخصات تنفيذية** لأهم النقاط والقرارات.
5. **تصدير** ملفات الترجمة المزامنة (SRT) أو نص التفريغ الكامل (TXT).

### لماذا تتمنى كل شركة وكل فرد الحصول عليه؟

- 💰 **توفير مال فلكي**: خدمات التفريغ والترجمة الاحترافية تدفع بالدقيقة وتكلف ثروات؛ هذا النظام ينجز كل شيء بتكلفة صفر.
- ⚡ **سرعة وإنتاجية فائقة**: تحويل ساعتين صوتية إلى نص مترجم ومؤرخ زمانياً في ثوانٍ معدودة دون تدخل بشري.
- 🔒 **السيادة والسرية المطلقة**: تسجيلاتك الحساسة لا تُشارك مع أي شركات معالجة بيانات خارجية.

---

## 🛠️ البنية التقنية (100% موارد مجانية)

| المكون | التقنية المجانية | الدور |
|---|---|---|
| محرك التشغيل السحابي | GitHub Actions / Hugging Face Spaces | خوادم مجانية لتشغيل النماذج |
| محرك التفريغ الصوتي | Hugging Face Inference API (Whisper OSS) | تحويل الصوت إلى نص مع طوابع زمنية |
| محرك الترجمة والتلخيص | Google Gemini API / Groq API | ترجمة دلالية + ملخص تنفيذي |
| قاعدة البيانات | Supabase (PostgreSQL Free Tier) | تخزين النصوص والسجلات |
| قناة الاستقبال والتسليم | Telegram Bot API + Streamlit | إدخال وإخراج فوري |

---

## 🏗️ البنية الهندسية (4 طبقات)

```
[إرسال رابط/ملف (تليجرام/ويب)]
                    │
                    ▼
[Hugging Face / Whisper API — تفريغ صوتي بطوابع زمنية]
                    │
                    ▼
[Google Gemini API — ترجمة + تحسين + تلخيص]
                    │
                    ▼
[Supabase — تخزين السجلات ──► إرسال SRT + TXT إلى تليجرام]
```

### 1. طبقة الالتقاط والتفريغ (`src/audio_extractor.py` + `src/stt_engine.py`)
- استخراج الصوت من الفيديو (yt-dlp + ffmpeg)
- تفريغ عبر Whisper على Hugging Face API أو محلياً
- إخراج مقاطع بطوابع زمنية دقيقة

### 2. العقل المترجم والملخص (`src/translator.py`)
- ترجمة دلالية عبر Gemini 1.5 Flash أو Groq LLaMA 3
- مراعاة السياق الثقافي والتقني
- توليد ملخص تنفيذي مهيكل

### 3. طبقة الأرشيف (`src/database.py`)
- تخزين في Supabase (PostgreSQL مجاني)
- بحث نصي كامل في كل السجلات السابقة
- تتبع تاريخ العمليات

### 4. طبقة التوصيل (`telegram_bot/bot.py` + `web_dashboard/app.py`)
- بوت تليجرام للتفاعل الفوري
- لوحة Streamlit للويب
- تصدير SRT + TXT + الملخص

---

## 🚀 التثبيت والتشغيل

### المتطلبات المسبقة
- Python 3.10 أو أحدث
- ffmpeg (لتشغيل معالجة الصوت)
- حسابات مجانية على: Hugging Face, Google AI Studio, Supabase, Telegram

### 1. استنساخ المشروع
```bash
git clone <repository-url>
cd PolyGlot-StreamBaran
```

### 2. تثبيت المتطلبات
```bash
pip install -r requirements.txt
# تثبيت ffmpeg على أوبونتو
sudo apt-get install -y ffmpeg
```

### 3. إعداد متغيرات البيئة
```bash
cp .env.example .env
# عدّل ملف .env وأضف مفاتيحك المجانية
```

### 4. تهيئة قاعدة بيانات Supabase
- أنشئ مشروعاً على [supabase.com](https://supabase.com)
- افتح SQL Editor ونفّذ محتوى `src/database.py` (متغير `SQL_SCHEMA`)

### 5. التشغيل

**تشغيل بوت تليجرام:**
```bash
python -m telegram_bot.bot
```

**تشغيل لوحة الويب Streamlit:**
```bash
cd web_dashboard
streamlit run app.py
```

**تشغيل من سطر الأوامر:**
```bash
python main.py --url "https://youtube.com/watch?v=..." --lang ar
python main.py --file path/to/audio.mp3 --lang en --provider groq
```

---

## 📡 الأوامر المتاحة

### سطر الأوامر (CLI)
```bash
python main.py [OPTIONS]

الخيارات:
  --url URL          رابط فيديو للمعالجة
  --file PATH        ملف صوتي/فيديو محلي
  --lang LANG        لغة الترجمة (ar, en, tr, ...) [افتراضي: ar]
  --no-summary       تخطّي التلخيص
  --provider NAME    gemini أو groq [افتراضي: gemini]
```

### بوت تليجرام
- `/start` - بدء التشغيل
- `/lang` - اختيار لغة الترجمة
- `/help` - المساعدة
- `/about` - عن المشروع
- أرسل رابطاً أو ملفاً للبدء

---

## 📁 بنية المشروع

```
PolyGlot-StreamBaran/
├── config.py                  # الإعدادات المركزية
├── main.py                    # المنسق الرئيسي (CLI + Pipeline)
├── requirements.txt           # متطلبات Python
├── .env.example               # نموذج متغيرات البيئة
├── README.md                  # هذا الملف
├── LICENSE                    # رخصة ملكية خاصة (Proprietary)
├── src/                       # الكود المصدري الأساسي
│   ├── __init__.py
│   ├── audio_extractor.py     # استخراج الصوت من الفيديو
│   ├── stt_engine.py          # محرك تفريغ الصوت (Whisper)
│   ├── translator.py          # محرك الترجمة والتلخيص
│   ├── database.py            # طبقة قاعدة البيانات (Supabase)
│   └── srt_generator.py       # مولّد ملفات SRT
├── telegram_bot/              # بوت تليجرام
│   ├── __init__.py
│   └── bot.py
├── web_dashboard/             # واجهة Streamlit
│   ├── app.py
│   └── requirements.txt
├── huggingface_space/         # ملفات النشر على HF Spaces
│   ├── app.py
│   ├── README.md
│   └── requirements.txt
├── github_actions/            # سير عمل GitHub Actions
│   └── workflow.yml
├── tests/                     # الاختبارات
│   └── test_system.py
├── docs/                      # الوثائق
│   ├── ARCHITECTURE.md
│   ├── INSTALLATION.md
│   └── USAGE.md
└── examples/                  # أمثلة
    └── sample_workflow.md
```

---

## 🌍 اللغات المدعومة

| الرمز | اللغة | الرمز | اللغة |
|---|---|---|---|
| ar | العربية | ko | الكورية |
| en | الإنجليزية | fa | الفارسية |
| tr | التركية | ur | الأردية |
| fr | الفرنسية | hi | الهندية |
| de | الألمانية | pt | البرتغالية |
| es | الإسبانية | nl | الهولندية |
| it | الإيطالية | sv | السويدية |
| ru | الروسية | pl | البولندية |
| zh | الصينية | id | الإندونيسية |
| ja | اليابانية | he | العبرية |

---

## 🔧 استكشاف الأخطاء

| المشكلة | الحل |
|---|---|
| `HF_TOKEN missing` | احصل على توكن مجاني من huggingface.co/settings/tokens |
| `GEMINI_API_KEY missing` | احصل عليه من aistudio.google.com/app/apikey |
| `ffmpeg not found` | ثبّته: `sudo apt install ffmpeg` أو `brew install ffmpeg` |
| `Supabase connection failed` | تحقق من URL و KEY في ملف .env |
| البوت لا يستجيب | تأكد من TELEGRAM_BOT_TOKEN وصلاحية الشبكة |

---

## 📞 الدعم والتواصل

للدعم الفني أو الاستفسارات أو طلب ميزات جديدة:

- 📧 **البريد:** Baranavisat@gmail.com
- 📱 **واتساب:** 00905313263722
- 👤 **المؤلف:** Baran Avisat

---

## 📜 الترخيص

هذا المشروع مرخّص برخصة ملكية خاصة (Proprietary — جميع الحقوق محفوظة). الاستخدام التجاري يتطلب إذناً خطياً من المؤلف. راجع ملف [LICENSE](LICENSE).

**© 2026 Baran Avisat. جميع الحقوق محفوظة.**


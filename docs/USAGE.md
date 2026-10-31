# 📖 دليل الاستخدام — PolyGlot-StreamBaran

**المؤلف:** Baran Avisat | **البريد:** Baranavisat@gmail.com | **واتساب:** 00905313263722

---

## السيناريو 1: ترجمة فيديو يوتيوب عبر تليجرام

1. افتح بوتك على تليجرام
2. أرسل الأمر `/lang` واختر اللغة (مثلاً: العربية)
3. أرسل رابط الفيديو:
   ```
   https://www.youtube.com/watch?v=dQw4w9WgXcQ
   ```
4. انتظر دقائق (حسب طول الفيديو)
5. ستصلك 3 رسائل:
   - 📄 ملف TXT بالنص المترجم
   - 🎬 ملف SRT جاهز للعرض
   - 📝 الملخص التنفيذي

---

## السيناريو 2: تفريغ ملف صوتي عبر واجهة الويب

1. افتح `http://localhost:8501`
2. اذهب لتبويب **📂 رفع ملف**
3. اختر اللغة من الشريط الجانبي
4. ارفع ملف MP3/WAV/MP4
5. اضغط **🚀 معالجة الملف**
6. حمّل النتائج بعد الانتهاء

---

## السيناريو 3: المعالجة المبرمجة (CLI)

```bash
# ترجمة فيديو إلى العربية
python main.py --url "https://youtube.com/watch?v=XXX" --lang ar

# تفريغ ملف محلي بدون تلخيص
python main.py --file meeting.mp3 --lang en --no-summary

# استخدام Groq بدلاً من Gemini
python main.py --url "..." --lang tr --provider groq
```

---

## أمثلة على المخرجات

### ملف SRT (subtitle.srt)
```
1
00:00:00,000 --> 00:00:03,500
مرحباً بكم في هذا الدرس التعليمي

2
00:00:03,500 --> 00:00:07,200
سنتعلم اليوم كيفية بناء تطبيقات الذكاء الاصطناعي

3
00:00:07,200 --> 00:00:11,000
باستخدام موارد مجانية بالكامل

============================================================
تم الإنشاء بواسطة: PolyGlot-StreamBaran v1.0.0
المؤلف: Baran Avisat
البريد: Baranavisat@gmail.com
واتساب: 00905313263722
© 2026 Baran Avisat. جميع الحقوق محفوظة.
============================================================
```

### الملخص التنفيذي
```
📝 الملخص التنفيذي:

الفكرة الرئيسية: يشرح الفيديو كيفية بناء تطبيقات ذكاء اصطناعي
بموارد مجانية بالكامل عبر منصات مفتوحة المصدر.

أهم النقاط:
• استخدام Hugging Face للحصول على نماذج مجانية
• الاستفادة من Gemini API للترجمة الذكية
• تخزين البيانات على Supabase مجاناً
• ربط كل المكونات عبر Python

التوصية: ابدأ بمشروع صغير ثم توسّع تدريجياً.
```

---

## نصائح متقدمة

### معالجة ملفات طويلة
النظام يقسّم تلقائياً الملفات التي تزيد عن 30 دقيقة. للتحكم:
```python
from src.audio_extractor import AudioExtractor
extractor = AudioExtractor()
segments = extractor.split_audio(audio_path, segment_minutes=15)
```

### تبديل نموذج Whisper
```env
# في .env
WHISPER_MODEL=openai/whisper-large-v3   # للأعلى دقة
# أو
WHISPER_MODEL=openai/whisper-base       # للأسرع
```

### البحث في السجلات السابقة
```python
from src.database import DatabaseManager
db = DatabaseManager()
results = db.search_records("ذكاء اصطناعي")
for r in results:
    print(r["file_name"], r["summary"])
```

---

**© 2026 Baran Avisat. للدعم: Baranavisat@gmail.com | 00905313263722**

"""
============================================================
 لوحة تحكم Streamlit - واجهة الويب
 المؤلف: Baran Avisat  |  Baranavisat@gmail.com
============================================================
 واجهة ويب تفاعلية لرفع الملفات والروابط، متابعة المعالجة،
 تصفح السجلات السابقة، وتنزيل الملفات الناتجة.
"""

import os
import sys
from pathlib import Path

# ضبط مسار المشروع
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from config import CONFIG

# محاولة استيراد المنسق
try:
    from main import PipelineOrchestrator
    PIPELINE_AVAILABLE = True
except Exception as e:
    PIPELINE_AVAILABLE = False
    PIPELINE_ERROR = str(e)


# ============================================================
# إعدادات الصفحة
# ============================================================
st.set_page_config(
    page_title=f"{CONFIG.PROJECT_NAME}",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# التنسيقات المخصصة
# ============================================================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .main-header h1 { color: white; margin: 0; }
    .main-header p { color: rgba(255,255,255,0.9); margin-top: 0.5rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        background-color: #f0f2f6;
        border-radius: 8px 8px 0 0;
    }
    .footer {
        text-align: center;
        padding: 1rem;
        margin-top: 2rem;
        background: #f8f9fa;
        border-radius: 8px;
        color: #6c757d;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# الرأس
# ============================================================
st.markdown(f"""
<div class="main-header">
    <h1>🌐 {CONFIG.PROJECT_NAME}</h1>
    <p>المنظومة الذاتية للترجمة، تفريغ الصوت، وتوليد الترجمات المرئية</p>
</div>
""", unsafe_allow_html=True)


# ============================================================
# الشريط الجانبي
# ============================================================
with st.sidebar:
    st.markdown("### ⚙️ الإعدادات")
    target_lang = st.selectbox(
        "🌍 لغة الترجمة",
        options=["ar", "en", "tr", "fr", "de", "es", "it", "ru", "zh", "ja", "ko", "fa"],
        format_func=lambda x: {
            "ar": "🇸🇦 العربية", "en": "🇬🇧 الإنجليزية", "tr": "🇹🇷 التركية",
            "fr": "🇫🇷 الفرنسية", "de": "🇩🇪 الألمانية", "es": "🇪🇸 الإسبانية",
            "it": "🇮🇹 الإيطالية", "ru": "🇷🇺 الروسية", "zh": "🇨🇳 الصينية",
            "ja": "🇯🇵 اليابانية", "ko": "🇰🇷 الكورية", "fa": "🇮🇷 الفارسية",
        }.get(x, x),
    )
    ai_provider = st.selectbox("🤖 محرك الذكاء", ["gemini", "groq"], format_func=lambda x: "Google Gemini" if x == "gemini" else "Groq (LLaMA 3)")
    generate_summary = st.checkbox("📝 توليد ملخص تنفيذي", value=True)

    st.markdown("---")
    st.markdown(f"### 👤 المؤلف\n**{CONFIG.AUTHOR_NAME}**\n\n📧 {CONFIG.AUTHOR_EMAIL}\n\n📱 {CONFIG.AUTHOR_WHATSAPP}")
    st.markdown(f"\n*{CONFIG.COPYRIGHT_NOTICE}*")


# ============================================================
# التبويبات
# ============================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "🎬 معالجة وسائط", "📂 رفع ملف", "🗂️ السجلات", "ℹ️ عن المشروع"
])


# --------------------------------------------------------
# تبويب: معالجة رابط
# --------------------------------------------------------
with tab1:
    st.markdown("### 🎬 معالجة رابط فيديو")
    url = st.text_input("🔗 أدخل رابط الفيديو (يوتيوب، فيسبوك، تويتر، إلخ):",
                        placeholder="https://www.youtube.com/watch?v=...")

    if st.button("🚀 ابدأ المعالجة", type="primary", use_container_width=True):
        if not url:
            st.warning("الرجاء إدخال رابط صحيح")
        elif not PIPELINE_AVAILABLE:
            st.error(f"تعذر تحميل المنظومة: {PIPELINE_ERROR}")
        else:
            with st.spinner("⏳ جارٍ المعالجة. قد يستغرق ذلك عدة دقائق..."):
                try:
                    pipeline = PipelineOrchestrator(ai_provider=ai_provider)
                    result = pipeline.process_url(url, target_lang, generate_summary)

                    st.success("✅ تمت المعالجة بنجاح!")

                    col1, col2, col3 = st.columns(3)
                    col1.metric("عدد المقاطع", result["segments_count"])
                    col2.metric("المدة (ث)", f"{result['duration_seconds']:.1f}")
                    col3.metric("اللغة", target_lang)

                    if result["summary"]:
                        st.markdown("### 📝 الملخص التنفيذي")
                        st.info(result["summary"])

                    st.markdown("### 📄 النص المترجم")
                    st.text_area("الترجمة", result["translated_text"], height=300)

                    # تنزيل الملفات
                    col_dl1, col_dl2 = st.columns(2)
                    srt_path = Path(result["srt_path"])
                    txt_path = Path(result["txt_path"])
                    if srt_path.exists():
                        col_dl1.download_button("⬇️ تحميل SRT", srt_path.read_bytes(), file_name=srt_path.name)
                    if txt_path.exists():
                        col_dl2.download_button("⬇️ تحميل TXT", txt_path.read_bytes(), file_name=txt_path.name)
                except Exception as e:
                    st.error(f"❌ خطأ: {e}")


# --------------------------------------------------------
# تبويب: رفع ملف
# --------------------------------------------------------
with tab2:
    st.markdown("### 📂 رفع ملف صوتي/مرئي")
    uploaded = st.file_uploader(
        "اختر ملفاً:", type=["mp3", "wav", "m4a", "ogg", "mp4", "mkv", "avi", "mov", "webm"]
    )
    if uploaded and st.button("🚀 معالجة الملف", type="primary"):
        if not PIPELINE_AVAILABLE:
            st.error(f"تعذر التحميل: {PIPELINE_ERROR}")
        else:
            temp_path = CONFIG.PATHS.temp_dir / uploaded.name
            with open(temp_path, "wb") as f:
                f.write(uploaded.getbuffer())

            with st.spinner("⏳ جارٍ المعالجة..."):
                try:
                    pipeline = PipelineOrchestrator(ai_provider=ai_provider)
                    result = pipeline.process_file(temp_path, target_lang, generate_summary)
                    st.success("✅ تمت المعالجة!")
                    if result["summary"]:
                        st.info(result["summary"])
                    st.text_area("النص المترجم", result["translated_text"], height=250)

                    srt_path = Path(result["srt_path"])
                    if srt_path.exists():
                        st.download_button("⬇️ تحميل SRT", srt_path.read_bytes(), file_name=srt_path.name)
                except Exception as e:
                    st.error(f"❌ خطأ: {e}")
                finally:
                    temp_path.unlink(missing_ok=True)


# --------------------------------------------------------
# تبويب: السجلات
# --------------------------------------------------------
with tab3:
    st.markdown("### 🗂️ السجلات السابقة")
    search_query = st.text_input("🔍 بحث في السجلات:")
    if st.button("عرض السجلات"):
        if not PIPELINE_AVAILABLE:
            st.warning("قاعدة البيانات غير متاحة")
        else:
            from src.database import DatabaseManager
            db = DatabaseManager()
            if search_query:
                records = db.search_records(search_query)
            else:
                records = db.get_recent_records(limit=20)

            if not records:
                st.info("لا توجد سجلات بعد")
            else:
                for rec in records:
                    with st.expander(f"📄 {rec.get('file_name', 'بدون اسم')} - {rec.get('created_at', '')}"):
                        if rec.get("summary"):
                            st.write(rec["summary"])
                        st.caption(f"اللغة: {rec.get('target_lang', '')} | المعرّف: {rec.get('id', '')}")


# --------------------------------------------------------
# تبويب: عن المشروع
# --------------------------------------------------------
with tab4:
    st.markdown(f"""
    ### ℹ️ عن {CONFIG.PROJECT_NAME}

    **{CONFIG.PROJECT_NAME}** هو نظام ذكي متكامل ومستقل لتحويل التسجيلات الصوتية
    ومقاطع الفيديو إلى نصوص دقيقة، تفريغ المحتوى مع التوقيت الزمني (SRT)،
    ترجمته فورياً إلى أي لغة، وتوليد ملخصات تنفيذية.

    #### 🛠️ البنية التقنية (100% موارد مجانية):
    | المكون | التقنية | الدور |
    |---|---|---|
    | محرك التشغيل | GitHub Actions / HF Spaces | خوادم مجانية |
    | تفريغ الصوت | Whisper (Hugging Face) | STT مجاني |
    | الترجمة والتلخيص | Gemini / Groq API | AI Brain |
    | قاعدة البيانات | Supabase (PostgreSQL) | تخزين مجاني |
    | واجهة التسليم | Telegram + Streamlit | UI مجاني |

    #### ✨ المزايا:
    - 💰 **تكلفة صفر**: لا تدفع دولاراً واحداً
    - ⚡ **سرعة فائقة**: ساعات صوت في ثوانٍ
    - 🔒 **سرية مطلقة**: بياناتك تبقى ملكك
    - 🌍 **دعم 12+ لغة**

    #### 📞 التواصل والدعم:
    - **المؤلف:** {CONFIG.AUTHOR_NAME}
    - **البريد:** {CONFIG.AUTHOR_EMAIL}
    - **واتساب:** {CONFIG.AUTHOR_WHATSAPP}

    ---
    *{CONFIG.COPYRIGHT_NOTICE}*
    """)


# ============================================================
# التذييل
# ============================================================
st.markdown(f"""
<div class="footer">
    <strong>{CONFIG.PROJECT_NAME}</strong> v{CONFIG.PROJECT_VERSION} | 
    المؤلف: {CONFIG.AUTHOR_NAME} | 
    {CONFIG.COPYRIGHT_NOTICE}
</div>
""", unsafe_allow_html=True)

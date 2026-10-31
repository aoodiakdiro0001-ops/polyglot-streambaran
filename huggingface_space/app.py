"""
============================================================
 تطبيق Hugging Face Space - واجهة Gradio
 المؤلف: Baran Avisat  |  Baranavisat@gmail.com
===========================================================
 واجهة مبسطة لـ Hugging Face Spaces باستخدام Gradio
 للنشر المجاني على السحابة.
"""

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import gradio as gr
from config import CONFIG

# محاولة استيراد المنسق
PIPELINE = None
PIPELINE_ERROR = None
try:
    from main import PipelineOrchestrator
    provider = "gemini" if CONFIG.KEYS.gemini else "groq"
    PIPELINE = PipelineOrchestrator(ai_provider=provider)
except Exception as e:
    PIPELINE_ERROR = str(e)


LANGUAGES = {
    "العربية": "ar", "English": "en", "Türkçe": "tr", "Français": "fr",
    "Deutsch": "de", "Español": "es", "Italiano": "it", "Русский": "ru",
    "中文": "zh", "日本語": "ja", "한국어": "ko", "فارسی": "fa",
}


def process_url(url, lang_name, generate_summary):
    """معالجة رابط وإرجاع النتائج."""
    if PIPELINE is None:
        return f"❌ خطأ في التهيئة: {PIPELINE_ERROR}", "", "", None
    if not url:
        return "⚠️ الرجاء إدخال رابط", "", "", None
    target_lang = LANGUAGES.get(lang_name, "ar")
    try:
        result = PIPELINE.process_url(url, target_lang, generate_summary)
        srt_path = result.get("srt_path")
        return (
            result.get("summary", "لا يوجد ملخص"),
            result.get("translated_text", ""),
            result.get("original_text", ""),
            srt_path if srt_path and Path(srt_path).exists() else None,
        )
    except Exception as e:
        return f"❌ خطأ: {e}", "", "", None


def process_file(file_obj, lang_name, generate_summary):
    """معالجة ملف مرفوع."""
    if PIPELINE is None:
        return f"❌ خطأ: {PIPELINE_ERROR}", "", "", None
    if file_obj is None:
        return "⚠️ لم يتم رفع ملف", "", "", None
    target_lang = LANGUAGES.get(lang_name, "ar")
    try:
        result = PIPELINE.process_file(Path(file_obj.name), target_lang, generate_summary)
        srt_path = result.get("srt_path")
        return (
            result.get("summary", ""),
            result.get("translated_text", ""),
            result.get("original_text", ""),
            srt_path if srt_path and Path(srt_path).exists() else None,
        )
    except Exception as e:
        return f"❌ خطأ: {e}", "", "", None


# ============================================================
# بناء الواجهة
# ============================================================
with gr.Blocks(
    title=CONFIG.PROJECT_NAME,
    theme=gr.themes.Soft(primary_hue="indigo", secondary_hue="purple"),
) as demo:

    gr.Markdown(f"""
    # 🌐 {CONFIG.PROJECT_NAME}
    **المنظومة الذاتية للترجمة، تفريغ الصوت، وتوليد الترجمات المرئية**

    تحويل التسجيلات الصوتية ومقاطع الفيديو إلى نصوص دقيقة مع طوابع زمنية،
    ترجمة فورية لأكثر من 12 لغة، وتوليد ملخصات تنفيذية — **100% مجاني**.
    """)

    with gr.Tab("🎬 معالجة رابط"):
        with gr.Row():
            url_input = gr.Textbox(label="🔗 رابط الفيديو", placeholder="https://youtube.com/watch?v=...")
            lang_input = gr.Dropdown(list(LANGUAGES.keys()), value="العربية", label="🌍 لغة الترجمة")
        summary_check = gr.Checkbox(value=True, label="📝 توليد ملخص تنفيذي")
        process_btn = gr.Button("🚀 ابدأ المعالجة", variant="primary")
        summary_out = gr.Textbox(label="📝 الملخص", lines=6)
        with gr.Row():
            translated_out = gr.Textbox(label="🌍 النص المترجم", lines=10)
            original_out = gr.Textbox(label="📄 النص الأصلي", lines=10)
        srt_file = gr.File(label="⬇️ ملف SRT")
        process_btn.click(process_url, [url_input, lang_input, summary_check],
                          [summary_out, translated_out, original_out, srt_file])

    with gr.Tab("📂 رفع ملف"):
        file_input = gr.File(label="📁 اختر ملفاً صوتياً/مرئياً")
        lang_input2 = gr.Dropdown(list(LANGUAGES.keys()), value="العربية", label="🌍 لغة الترجمة")
        summary_check2 = gr.Checkbox(value=True, label="📝 ملخص")
        process_btn2 = gr.Button("🚀 معالجة", variant="primary")
        summary_out2 = gr.Textbox(label="📝 الملخص", lines=6)
        translated_out2 = gr.Textbox(label="🌍 النص المترجم", lines=10)
        srt_file2 = gr.File(label="⬇️ ملف SRT")
        process_btn2.click(process_file, [file_input, lang_input2, summary_check2],
                           [summary_out2, translated_out2, gr.Textbox(visible=False), srt_file2])

    gr.Markdown(f"""
    ---
    **👤 المؤلف:** {CONFIG.AUTHOR_NAME} | 📧 {CONFIG.AUTHOR_EMAIL} | 📱 {CONFIG.AUTHOR_WHATSAPP}

    {CONFIG.COPYRIGHT_NOTICE}
    """)


if __name__ == "__main__":
    demo.launch()

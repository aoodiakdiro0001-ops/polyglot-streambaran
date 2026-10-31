"""
============================================================
 العقل المترجم والملخص (AI Translation & Summarization Core)
 المؤلف: Baran Avisat  |  Baranavisat@gmail.com
============================================================
 يستخدم Google Gemini API أو Groq API (مجاناً) لترجمة
 النصوص دلالياً مع مراعاة السياق، وتوليد ملخصات تنفيذية.
"""

import os
import logging
from typing import Optional

from config import CONFIG

logger = logging.getLogger(__name__)


class AITranslator:
    """محرّك الترجمة والتلخيص الذكي."""

    def __init__(self, provider: str = "gemini"):
        """
        Args:
            provider: "gemini" أو "groq"
        """
        self.provider = provider.lower()
        self.target_lang = CONFIG.MODELS.default_target_lang
        self.client = None
        self._init_client()

    # --------------------------------------------------------
    # تهيئة العميل المناسب
    # --------------------------------------------------------
    def _init_client(self):
        if self.provider == "gemini":
            self._init_gemini()
        elif self.provider == "groq":
            self._init_groq()
        else:
            raise ValueError(f"مزود غير مدعوم: {self.provider}")

    def _init_gemini(self):
        api_key = CONFIG.KEYS.gemini
        if not api_key:
            raise ValueError("GEMINI_API_KEY مطلوب")
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(CONFIG.MODELS.gemini_model)
            logger.info("تم تهيئة Google Gemini API بنجاح")
        except ImportError:
            raise RuntimeError("ثبّت الحزمة: pip install google-generativeai")

    def _init_groq(self):
        api_key = CONFIG.KEYS.groq
        if not api_key:
            raise ValueError("GROQ_API_KEY مطلوب")
        try:
            from groq import Groq
            self.client = Groq(api_key=api_key)
            logger.info("تم تهيئة Groq API بنجاح")
        except ImportError:
            raise RuntimeError("ثبّت الحزمة: pip install groq")

    # --------------------------------------------------------
    # ترجمة نص كامل
    # --------------------------------------------------------
    def translate(self, text: str, target_lang: Optional[str] = None,
                  source_lang: str = "auto") -> str:
        """
        ترجمة نص مع مراعاة السياق الثقافي والتقني.
        
        Args:
            text: النص المراد ترجمته
            target_lang: رمز اللغة الهدف (ar, en, tr, ...)
            source_lang: لغة المصدر (auto للكشف التلقائي)
        """
        if not text.strip():
            return ""

        target = target_lang or self.target_lang
        prompt = self._build_translation_prompt(text, target, source_lang)

        try:
            result = self._call_ai(prompt)
            logger.info(f"تمت ترجمة {len(text)} حرف إلى {target}")
            return result.strip()
        except Exception as e:
            logger.error(f"فشل الترجمة: {e}")
            return text  # إرجاع النص الأصلي عند الفشل

    # --------------------------------------------------------
    # توليد ملخص تنفيذي
    # --------------------------------------------------------
    def summarize(self, text: str, max_words: int = 250,
                  lang: Optional[str] = None) -> str:
        """توليد ملخص تنفيذي يركّز على أهم النقاط والقرارات."""
        if not text.strip():
            return ""

        target_lang = lang or self.target_lang
        prompt = (
            f"أنت مساعد محترف في تلخيص المحتوى. اقرأ النص التالي بدقة، "
            f"ثم اكتب ملخصاً تنفيذياً احترافياً لا يتجاوز {max_words} كلمة، "
            f"يحتوي على:\n"
            f"1) الفكرة الرئيسية في جملتين.\n"
            f"2) أهم 3-7 نقاط أو قرارات بشكل نقطي واضح.\n"
            f"3) توصية ختامية واحدة إن وجدت.\n\n"
            f"اكتب الملخص باللغة: {target_lang}.\n\n"
            f"النص:\n\"\"\"\n{text}\n\"\"\""
        )

        try:
            result = self._call_ai(prompt)
            logger.info(f"تم توليد ملخص ({len(result)} حرف)")
            return result.strip()
        except Exception as e:
            logger.error(f"فشل التلخيص: {e}")
            return ""

    # --------------------------------------------------------
    # ترجمة وتلخيص في خطوة واحدة
    # --------------------------------------------------------
    def translate_and_summarize(self, text: str, target_lang: Optional[str] = None) -> dict:
        """يترجم النص ثم يولّد ملخصاً للنسخة المترجمة."""
        translated = self.translate(text, target_lang)
        summary = self.summarize(translated, lang=target_lang)
        return {
            "original": text,
            "translated": translated,
            "summary": summary,
            "target_lang": target_lang or self.target_lang,
        }

    # --------------------------------------------------------
    # ترجمة مقطع مع الحفاظ على الطابع الزمني
    # --------------------------------------------------------
    def translate_segment(self, text: str, target_lang: Optional[str] = None) -> str:
        """ترجمة مقطع قصير مع الحفاظ على البنية."""
        target = target_lang or self.target_lang
        prompt = (
            f"ترجم الجملة التالية إلى {target} بأسلوب طبيعي وسليم. "
            f"أعِد فقط الترجمة بدون أي شرح أو علامات اقتباس:\n\n{text}"
        )
        try:
            return self._call_ai(prompt).strip()
        except Exception:
            return text

    # --------------------------------------------------------
    # بناء برومت الترجمة
    # --------------------------------------------------------
    def _build_translation_prompt(self, text: str, target: str, source: str) -> str:
        lang_name = self._lang_code_to_name(target)
        source_hint = "اللغة الأصلية" if source == "auto" else self._lang_code_to_name(source)
        return (
            f"أنت مترجم محترف. ترجم النص التالي من {source_hint} إلى {lang_name}.\n"
            f"القواعد:\n"
            f"1) حافظ على المعنى الدلالي والسياق التقني.\n"
            f"2) استخدم لغة طبيعية وسليمة نحوياً.\n"
            f"3) حافظ على الأسماء العلمية والأعلام كما هي.\n"
            f"4) لا تضف أي تعليقات أو شروحات إضافية.\n"
            f"5) أعِد فقط النص المترجم.\n\n"
            f"النص:\n\"\"\"\n{text}\n\"\"\""
        )

    # --------------------------------------------------------
    # استدعاء نموذج الذكاء الاصطناعي
    # --------------------------------------------------------
    def _call_ai(self, prompt: str) -> str:
        if self.provider == "gemini":
            return self._call_gemini(prompt)
        return self._call_groq(prompt)

    def _call_gemini(self, prompt: str) -> str:
        response = self.client.generate_content(prompt)
        return response.text

    def _call_groq(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=CONFIG.MODELS.groq_model,
            messages=[
                {"role": "system", "content": "أنت مساعد ذكي ومترجم محترف."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=4096,
        )
        return response.choices[0].message.content

    # --------------------------------------------------------
    # تحويل رمز اللغة إلى اسمها
    # --------------------------------------------------------
    @staticmethod
    def _lang_code_to_name(code: str) -> str:
        names = {
            "ar": "العربية", "en": "الإنجليزية", "tr": "التركية",
            "fr": "الفرنسية", "de": "الألمانية", "es": "الإسبانية",
            "it": "الإيطالية", "ru": "الروسية", "zh": "الصينية",
            "ja": "اليابانية", "ko": "الكورية", "fa": "الفارسية",
            "ur": "الأردية", "hi": "الهندية", "pt": "البرتغالية",
            "nl": "الهولندية", "sv": "السويدية", "pl": "البولندية",
            "id": "الإندونيسية", "he": "العبرية",
        }
        return names.get(code, code)

"""
============================================================
 PolyGlot-StreamBaran | مركز الإعدادات الرئيسي
 المؤلف: Baran Avisat
 البريد: Baranavisat@gmail.com
 واتساب: 00905313263722
============================================================
 هذا الملف يحمل كل الإعدادات المركزية للمشروع ويُستدعى
 من كل الطبقات الأخرى لضمان تناغم المنظومة.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

# ============================================================
# معلومات المالك وحقوق الملكية
# ============================================================
AUTHOR_NAME: str = "Baran Avisat"
AUTHOR_EMAIL: str = "Baranavisat@gmail.com"
AUTHOR_WHATSAPP: str = "00905313263722"
PROJECT_NAME: str = "PolyGlot-StreamBaran"
PROJECT_VERSION: str = "1.0.0"
COPYRIGHT_NOTICE: str = (
    f"© {os.getenv('CURRENT_YEAR', '2026')} {AUTHOR_NAME}. "
    "جميع الحقوق محفوظة. الاستخدام التجاري يتطلب إذناً خطياً من المالك."
)


# ============================================================
# إعدادات API Keys
# ============================================================
@dataclass
class APIKeys:
    """حاوية كل مفاتيح الـ APIs المجانية."""
    gemini: str = os.getenv("GEMINI_API_KEY", "")
    groq: str = os.getenv("GROQ_API_KEY", "")
    huggingface: str = os.getenv("HF_TOKEN", "")
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_KEY", "")
    telegram_bot: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "")


# ============================================================
# إعدادات النماذج
# ============================================================
@dataclass
class ModelConfig:
    """إعدادات نماذج الذكاء الاصطناعي."""
    whisper_model: str = os.getenv("DEFAULT_WHISPER_MODEL", "base")
    hf_whisper_model: str = os.getenv("WHISPER_MODEL", "openai/whisper-large-v3")
    gemini_model: str = "gemini-1.5-flash"
    groq_model: str = "llama3-70b-8192"
    default_target_lang: str = os.getenv("DEFAULT_TARGET_LANG", "ar")
    max_file_size_mb: int = int(os.getenv("MAX_FILE_SIZE_MB", "500"))


# ============================================================
# إعدادات المسارات
# ============================================================
@dataclass
class PathConfig:
    """إعدادات مسارات الملفات المؤقتة والناتجة."""
    base_dir: Path = Path(__file__).parent
    temp_dir: Path = Path(os.getenv("TEMP_DIR", "./temp"))
    output_dir: Path = Path(os.getenv("OUTPUT_DIR", "./output"))
    logs_dir: Path = Path("./logs")

    def ensure_dirs(self) -> None:
        """إنشاء كل المجلدات المطلوبة تلقائياً."""
        for d in (self.temp_dir, self.output_dir, self.logs_dir):
            d.mkdir(parents=True, exist_ok=True)


# ============================================================
# إعدادات الترجمة
# ============================================================
@dataclass
class TranslationConfig:
    """إعدادات الترجمة والتلخيص."""
    supported_languages: list = field(default_factory=lambda: [
        "ar", "en", "tr", "fr", "de", "es", "it", "ru", "zh", "ja",
        "ko", "fa", "ur", "hi", "pt", "nl", "sv", "pl", "id", "he"
    ])
    summary_max_words: int = 250
    translation_chunk_size: int = 1500  # عدد الأحرف لكل قطعة ترجمة


# ============================================================
# الإعدادات الموحدة
# ============================================================
class Config:
    """الإعدادات الموحدة للمشروع كاملاً."""
    KEYS = APIKeys()
    MODELS = ModelConfig()
    PATHS = PathConfig()
    TRANSLATION = TranslationConfig()
    # معلومات المالك (إعادة تصديرها للوصول الموحد)
    AUTHOR_NAME = AUTHOR_NAME
    AUTHOR_EMAIL = AUTHOR_EMAIL
    AUTHOR_WHATSAPP = AUTHOR_WHATSAPP
    PROJECT_NAME = PROJECT_NAME
    PROJECT_VERSION = PROJECT_VERSION
    COPYRIGHT_NOTICE = COPYRIGHT_NOTICE

    # التهيئة عند بدء التشغيل
    PATHS.ensure_dirs()

    @classmethod
    def get_footer(cls) -> str:
        """تذييل حقوق الملكية المُدمج في كل ملفات الإخراج."""
        return (
            f"\n\n{'=' * 60}\n"
            f"تم الإنشاء بواسطة: {PROJECT_NAME} v{PROJECT_VERSION}\n"
            f"المؤلف: {AUTHOR_NAME}\n"
            f"البريد: {AUTHOR_EMAIL}\n"
            f"واتساب: {AUTHOR_WHATSAPP}\n"
            f"{COPYRIGHT_NOTICE}\n"
            f"{'=' * 60}\n"
        )

    @classmethod
    def validate(cls) -> list:
        """التحقق من توفر المفاتيح الأساسية. يعيد قائمة بالنواقص."""
        missing = []
        if not cls.KEYS.gemini and not cls.KEYS.groq:
            missing.append("GEMINI_API_KEY أو GROQ_API_KEY")
        if not cls.KEYS.huggingface:
            missing.append("HF_TOKEN")
        if not cls.KEYS.supabase_url or not cls.KEYS.supabase_key:
            missing.append("SUPABASE_URL و SUPABASE_KEY")
        if not cls.KEYS.telegram_bot:
            missing.append("TELEGRAM_BOT_TOKEN")
        return missing


# تصدير مختصر
CONFIG = Config

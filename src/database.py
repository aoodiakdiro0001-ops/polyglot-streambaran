"""
============================================================
 طبقة الأرشفة والتخزين (Persistence Layer)
 المؤلف: Baran Avisat  |  Baranavisat@gmail.com
============================================================
 تخزين النصوص المفرغة، الترجمات، ملفات SRT، وسجلات المعالجة
 في قاعدة بيانات Supabase (PostgreSQL مجانية بالكامل).
"""

import logging
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, asdict

from config import CONFIG

logger = logging.getLogger(__name__)


@dataclass
class ProcessRecord:
    """سجل عملية معالجة واحدة."""
    file_name: str
    source_lang: str
    target_lang: str
    duration_seconds: float
    segments_count: int
    original_text: str
    translated_text: str
    summary: str
    srt_content: str
    created_at: str = None
    author: str = CONFIG.AUTHOR_NAME

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()


class DatabaseManager:
    """مدير قاعدة البيانات Supabase."""

    TABLE_NAME = "transcription_records"

    def __init__(self):
        self.client = None
        self._init_client()

    def _init_client(self):
        url = CONFIG.KEYS.supabase_url
        key = CONFIG.KEYS.supabase_key
        if not url or not key:
            logger.warning("Supabase غير مُعد. ستعمل الطبقة في وضع عدم الاتصال.")
            return
        try:
            from supabase import create_client
            self.client = create_client(url, key)
            logger.info("تم الاتصال بـ Supabase بنجاح")
        except ImportError:
            logger.error("ثبّت الحزمة: pip install supabase")
        except Exception as e:
            logger.error(f"فشل الاتصال بـ Supabase: {e}")

    # --------------------------------------------------------
    # حفظ سجل عملية معالجة كامل
    # --------------------------------------------------------
    def save_record(self, record: ProcessRecord) -> Optional[str]:
        """يحفظ السجل في قاعدة البيانات ويعيد المعرّف."""
        if self.client is None:
            logger.warning("القاعدة غير متصلة. تم تخطي الحفظ.")
            return None

        try:
            data = asdict(record)
            response = self.client.table(self.TABLE_NAME).insert(data).execute()
            record_id = response.data[0].get("id") if response.data else None
            logger.info(f"تم حفظ السجل بالمعرّف: {record_id}")
            return record_id
        except Exception as e:
            logger.error(f"فشل حفظ السجل: {e}")
            return None

    # --------------------------------------------------------
    # استرجاع سجل بالمعرّف
    # --------------------------------------------------------
    def get_record(self, record_id: str) -> Optional[dict]:
        if self.client is None:
            return None
        try:
            response = (
                self.client.table(self.TABLE_NAME)
                .select("*")
                .eq("id", record_id)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"فشل الاسترجاع: {e}")
            return None

    # --------------------------------------------------------
    # البحث في كل السجلات
    # --------------------------------------------------------
    def search_records(self, query: str, limit: int = 20) -> list:
        """بحث نصي داخل النصوص المفرغة والمترجمة."""
        if self.client is None:
            return []
        try:
            response = (
                self.client.table(self.TABLE_NAME)
                .select("id, file_name, summary, created_at")
                .or_(f"original_text.ilike.%{query}%,translated_text.ilike.%{query}%")
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"فشل البحث: {e}")
            return []

    # --------------------------------------------------------
    # استرجاع آخر N سجل
    # --------------------------------------------------------
    def get_recent_records(self, limit: int = 10) -> list:
        if self.client is None:
            return []
        try:
            response = (
                self.client.table(self.TABLE_NAME)
                .select("id, file_name, target_lang, duration_seconds, created_at")
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"فشل استرجاع السجلات: {e}")
            return []

    # --------------------------------------------------------
    # حذف سجل
    # --------------------------------------------------------
    def delete_record(self, record_id: str) -> bool:
        if self.client is None:
            return False
        try:
            self.client.table(self.TABLE_NAME).delete().eq("id", record_id).execute()
            logger.info(f"تم حذف السجل: {record_id}")
            return True
        except Exception as e:
            logger.error(f"فشل الحذف: {e}")
            return False


# ============================================================
# سكريبت إنشاء الجدول في Supabase (يشغّل يدوياً مرة واحدة)
# ============================================================
SQL_SCHEMA = """
-- جدول سجلات التفريغ والترجمة
CREATE TABLE IF NOT EXISTS transcription_records (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_name       TEXT NOT NULL,
    source_lang     TEXT NOT NULL,
    target_lang     TEXT NOT NULL,
    duration_seconds FLOAT DEFAULT 0,
    segments_count  INTEGER DEFAULT 0,
    original_text   TEXT,
    translated_text TEXT,
    summary         TEXT,
    srt_content     TEXT,
    author          TEXT DEFAULT 'Baran Avisat',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- فهرسة للبحث السريع
CREATE INDEX IF NOT EXISTS idx_transcription_created
    ON transcription_records (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_transcription_search
    ON transcription_records USING gin (to_tsvector('simple', original_text || ' ' || translated_text));

-- تفعيل Row Level Security
ALTER TABLE transcription_records ENABLE ROW LEVEL SECURITY;

-- سياسة السماح للجميع بالقراءة والكتابة (عدّلها حسب احتياجك)
CREATE POLICY "allow_all" ON transcription_records
    FOR ALL USING (true) WITH CHECK (true);
"""

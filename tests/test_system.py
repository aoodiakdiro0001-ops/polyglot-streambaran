"""
============================================================
 اختبارات المنظومة - PolyGlot-StreamBaran
 المؤلف: Baran Avisat  |  Baranavisat@gmail.com
============================================================
"""

import os
import sys
import pytest
from pathlib import Path

# ضبط المسار
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import CONFIG


# ============================================================
# اختبارات الإعدادات
# ============================================================
class TestConfig:
    def test_author_info(self):
        assert CONFIG.AUTHOR_NAME == "Baran Avisat"
        assert CONFIG.AUTHOR_EMAIL == "Baranavisat@gmail.com"
        assert CONFIG.AUTHOR_WHATSAPP == "00905313263722"

    def test_project_name(self):
        assert CONFIG.PROJECT_NAME == "PolyGlot-StreamBaran"
        assert CONFIG.PROJECT_VERSION == "1.0.0"

    def test_directories_created(self):
        assert CONFIG.PATHS.temp_dir.exists()
        assert CONFIG.PATHS.output_dir.exists()
        assert CONFIG.PATHS.logs_dir.exists()

    def test_supported_languages(self):
        assert "ar" in CONFIG.TRANSLATION.supported_languages
        assert "en" in CONFIG.TRANSLATION.supported_languages
        assert "tr" in CONFIG.TRANSLATION.supported_languages
        assert len(CONFIG.TRANSLATION.supported_languages) >= 12

    def test_footer_contains_author(self):
        footer = CONFIG.get_footer()
        assert "Baran Avisat" in footer
        assert "Baranavisat@gmail.com" in footer


# ============================================================
# اختبارات محرك التفريغ الصوتي (STT)
# ============================================================
class TestSTTEngine:
    def test_segment_to_srt_block(self):
        from src.stt_engine import TranscriptSegment
        seg = TranscriptSegment(start=1.5, end=3.0, text="مرحبا")
        block = seg.to_srt_block(1)
        assert "1" in block
        assert "00:00:01,500 --> 00:00:03,000" in block
        assert "مرحبا" in block

    def test_time_formatting(self):
        from src.stt_engine import TranscriptSegment
        assert TranscriptSegment._format_time(0) == "00:00:00,000"
        assert TranscriptSegment._format_time(61.5) == "00:01:01,500"
        assert TranscriptSegment._format_time(3661.25) == "01:01:01,250"


# ============================================================
# اختبارات مولّد SRT
# ============================================================
class TestSRTGenerator:
    def test_generate_srt(self, tmp_path):
        from src.stt_engine import TranscriptSegment
        from src.srt_generator import SRTGenerator

        segments = [
            TranscriptSegment(start=0, end=2, text="الأول"),
            TranscriptSegment(start=2, end=4, text="الثاني"),
            TranscriptSegment(start=4, end=6, text="الثالث"),
        ]
        output = tmp_path / "test.srt"
        SRTGenerator.generate(segments, output)

        assert output.exists()
        content = output.read_text(encoding="utf-8")
        assert "الأول" in content
        assert "الثاني" in content
        assert "الثالث" in content
        assert "Baran Avisat" in content  # تذييل حقوق الملكية


# ============================================================
# اختبارات محرك الترجمة (مع تجاوز عند عدم توفر المفاتيح)
# ============================================================
class TestTranslator:
    def test_lang_code_to_name(self):
        from src.translator import AITranslator
        assert AITranslator._lang_code_to_name("ar") == "العربية"
        assert AITranslator._lang_code_to_name("en") == "الإنجليزية"
        assert AITranslator._lang_code_to_name("unknown") == "unknown"

    def test_translation_prompt(self):
        from src.translator import AITranslator
        # _build_translation_prompt is an instance method (uses self.target_lang)
        # نتحقق من المنطق عبر فحص برومت التلخيص الثابت بدلاً من ذلك
        # أو بناء نسخة افتراضية بدون تهيئة العميل
        import inspect
        sig = inspect.signature(AITranslator._build_translation_prompt)
        params = list(sig.parameters.keys())
        assert "text" in params
        assert "target" in params
        assert "source" in params


# ============================================================
# اختبارات استخراج الصوت
# ============================================================
class TestAudioExtractor:
    def test_url_validation(self):
        from src.audio_extractor import AudioExtractor
        assert AudioExtractor._is_valid_url("https://youtube.com/watch?v=123") is True
        assert AudioExtractor._is_valid_url("not-a-url") is False
        assert AudioExtractor._is_valid_url("") is False


# ============================================================
# اختبارات قاعدة البيانات
# ============================================================
class TestDatabase:
    def test_process_record_creation(self):
        from src.database import ProcessRecord
        record = ProcessRecord(
            file_name="test.mp3",
            source_lang="en",
            target_lang="ar",
            duration_seconds=60.0,
            segments_count=10,
            original_text="Hello",
            translated_text="مرحبا",
            summary="ملخص",
            srt_content="1\n00:00:00,000 --> 00:00:02,000\nمرحبا\n",
        )
        assert record.file_name == "test.mp3"
        assert record.author == "Baran Avisat"
        assert record.created_at is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

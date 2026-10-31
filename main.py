"""
============================================================
 المنسق الرئيسي (Main Pipeline Orchestrator)
 المؤلف: Baran Avisat  |  Baranavisat@gmail.com
============================================================
 يربط كل الطبقات الأربع في مسار واحد متكامل:
 إدخال -> تفريغ -> ترجمة/تلخيص -> تخزين -> تسليم
"""

import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

from config import CONFIG
from src.audio_extractor import AudioExtractor
from src.stt_engine import STTEngine, TranscriptSegment
from src.translator import AITranslator
from src.database import DatabaseManager, ProcessRecord
from src.srt_generator import SRTGenerator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(CONFIG.PATHS.logs_dir / "pipeline.log", encoding="utf-8"),
    ]
)
logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    """المنسّق الرئيسي لمسار المعالجة الكامل."""

    def __init__(self, ai_provider: str = "gemini", use_hf_api: bool = True):
        """
        Args:
            ai_provider: "gemini" أو "groq"
            use_hf_api: استخدام Hugging Face API بدلاً من النموذج المحلي
        """
        self.extractor = AudioExtractor()
        self.stt = STTEngine(use_hf_api=use_hf_api)
        self.translator = AITranslator(provider=ai_provider)
        self.db = DatabaseManager()
        self.srt_gen = SRTGenerator()

    # --------------------------------------------------------
    # معالجة رابط فيديو (يوتيوب، فيسبوك، ...)
    # --------------------------------------------------------
    def process_url(
        self,
        url: str,
        target_lang: str = "ar",
        generate_summary: bool = True,
        output_name: Optional[str] = None,
    ) -> dict:
        """
        المعالجة الكاملة من رابط فيديو.
        
        Returns:
            قاموس يحوي: نص أصلي، نص مترجم، ملخص، SRT، ID السجل
        """
        logger.info(f"=== بدء المعالجة من رابط: {url} ===")
        output_name = output_name or f"url_{int(datetime.now().timestamp())}"

        # 1) استخراج الصوت
        audio_path = self.extractor.extract_from_url(url, output_name)

        # 2) التفريغ
        segments = self.stt.transcribe(audio_path)
        original_text = self.stt.segments_to_text(segments)
        logger.info(f"تم تفريغ {len(segments)} مقطع")

        # 3) الترجمة مقطعاً بمقطع للحفاظ على الطوابع الزمنية
        translated_segments = []
        for seg in segments:
            translated = self.translator.translate_segment(seg.text, target_lang)
            translated_segments.append(TranscriptSegment(
                start=seg.start, end=seg.end, text=translated
            ))

        translated_text = self.stt.segments_to_text(translated_segments)

        # 4) التلخيص
        summary = ""
        if generate_summary:
            summary = self.translator.summarize(original_text, lang=target_lang)

        # 5) توليد ملفات SRT و TXT
        srt_path = CONFIG.PATHS.output_dir / f"{output_name}.srt"
        txt_path = CONFIG.PATHS.output_dir / f"{output_name}.txt"
        self.srt_gen.generate(translated_segments, srt_path)
        self.srt_gen.export_txt(translated_segments, txt_path)

        srt_content = srt_path.read_text(encoding="utf-8")

        # 6) الحفظ في قاعدة البيانات
        record = ProcessRecord(
            file_name=output_name,
            source_lang="auto",
            target_lang=target_lang,
            duration_seconds=segments[-1].end if segments else 0,
            segments_count=len(segments),
            original_text=original_text,
            translated_text=translated_text,
            summary=summary,
            srt_content=srt_content,
        )
        record_id = self.db.save_record(record)

        logger.info(f"=== اكتملت المعالجة بنجاح ===")
        return {
            "record_id": record_id,
            "original_text": original_text,
            "translated_text": translated_text,
            "summary": summary,
            "srt_path": str(srt_path),
            "txt_path": str(txt_path),
            "segments_count": len(segments),
            "duration_seconds": record.duration_seconds,
        }

    # --------------------------------------------------------
    # معالجة ملف صوتي/فيديو محلي
    # --------------------------------------------------------
    def process_file(
        self,
        file_path: Path,
        target_lang: str = "ar",
        generate_summary: bool = True,
    ) -> dict:
        """المعالجة الكاملة من ملف محلي."""
        file_path = Path(file_path)
        logger.info(f"=== بدء المعالجة من ملف: {file_path.name} ===")

        # 1) استخراج/تحويل الصوت
        audio_path = self.extractor.extract_from_file(file_path)

        # 2) التفريغ
        segments = self.stt.transcribe(audio_path)
        original_text = self.stt.segments_to_text(segments)

        # 3) الترجمة مقطعاً بمقطع
        translated_segments = []
        for seg in segments:
            translated = self.translator.translate_segment(seg.text, target_lang)
            translated_segments.append(TranscriptSegment(
                start=seg.start, end=seg.end, text=translated
            ))
        translated_text = self.stt.segments_to_text(translated_segments)

        # 4) التلخيص
        summary = ""
        if generate_summary:
            summary = self.translator.summarize(original_text, lang=target_lang)

        # 5) تصدير
        output_name = file_path.stem
        srt_path = CONFIG.PATHS.output_dir / f"{output_name}.srt"
        txt_path = CONFIG.PATHS.output_dir / f"{output_name}.txt"
        self.srt_gen.generate(translated_segments, srt_path)
        self.srt_gen.export_txt(translated_segments, txt_path)

        srt_content = srt_path.read_text(encoding="utf-8")

        # 6) قاعدة البيانات
        record = ProcessRecord(
            file_name=file_path.name,
            source_lang="auto",
            target_lang=target_lang,
            duration_seconds=segments[-1].end if segments else 0,
            segments_count=len(segments),
            original_text=original_text,
            translated_text=translated_text,
            summary=summary,
            srt_content=srt_content,
        )
        record_id = self.db.save_record(record)

        logger.info(f"=== اكتملت المعالجة بنجاح ===")
        return {
            "record_id": record_id,
            "original_text": original_text,
            "translated_text": translated_text,
            "summary": summary,
            "srt_path": str(srt_path),
            "txt_path": str(txt_path),
            "segments_count": len(segments),
            "duration_seconds": record.duration_seconds,
        }


# ============================================================
# نقطة الدخول من سطر الأوامر (CLI)
# ============================================================
if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="PolyGlot-StreamBaran - المنظومة الذاتية للترجمة وتفريغ الصوت",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            f"المؤلف: {CONFIG.AUTHOR_NAME}\n"
            f"البريد: {CONFIG.AUTHOR_EMAIL}\n"
            f"واتساب: {CONFIG.AUTHOR_WHATSAPP}\n"
            f"{CONFIG.COPYRIGHT_NOTICE}"
        ),
    )
    parser.add_argument("--url", help="رابط الفيديو للمعالجة")
    parser.add_argument("--file", help="مسار ملف صوتي/فيديو محلي")
    parser.add_argument("--lang", default="ar", help="لغة الترجمة الهدف (افتراضي: ar)")
    parser.add_argument("--no-summary", action="store_true", help="تخطّي التلخيص")
    parser.add_argument("--provider", default="gemini", choices=["gemini", "groq"])

    args = parser.parse_args()
    if not args.url and not args.file:
        parser.print_help()
        sys.exit(1)

    pipeline = PipelineOrchestrator(ai_provider=args.provider)

    if args.url:
        result = pipeline.process_url(args.url, args.lang, not args.no_summary)
    else:
        result = pipeline.process_file(Path(args.file), args.lang, not args.no_summary)

    print("\n" + "=" * 60)
    print("تمت المعالجة بنجاح!")
    print(f"  عدد المقاطع: {result['segments_count']}")
    print(f"  المدة: {result['duration_seconds']:.1f} ثانية")
    print(f"  ملف SRT: {result['srt_path']}")
    print(f"  ملف TXT: {result['txt_path']}")
    if result["summary"]:
        print(f"\nالملخص:\n{result['summary']}")
    print(CONFIG.get_footer())

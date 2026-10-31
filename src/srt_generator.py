"""
============================================================
 مولّد ملفات SRT (SubRip Subtitle Generator)
 المؤلف: Baran Avisat  |  Baranavisat@gmail.com
============================================================
 يحوّل المقاطع المفرغة مع طوابعها الزمنية إلى ملف SRT
 متوافق مع كل منصات العرض (YouTube, VLC, Premiere, ...).
"""

import logging
from pathlib import Path
from typing import List

from src.stt_engine import TranscriptSegment
from config import CONFIG

logger = logging.getLogger(__name__)


class SRTGenerator:
    """مولّد ملفات الترجمة بصيغة SRT."""

    @staticmethod
    def generate(segments: List[TranscriptSegment], output_path: Path) -> Path:
        """
        توليد ملف SRT من قائمة المقاطع.
        
        Args:
            segments: قائمة المقاطع مع الطوابع الزمنية
            output_path: مسار الملف الناتج
        
        Returns:
            مسار ملف SRT المنشأ
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        srt_lines = []
        for i, seg in enumerate(segments, start=1):
            block = seg.to_srt_block(i)
            srt_lines.append(block)

        # إضافة تذييل حقوق الملكية كتعليق SRT
        srt_lines.append(CONFIG.get_footer())

        content = "\n".join(srt_lines)
        output_path.write_text(content, encoding="utf-8")
        logger.info(f"تم إنشاء ملف SRT: {output_path} ({len(segments)} مقطع)")
        return output_path

    @staticmethod
    def generate_from_translated(
        original_segments: List[TranscriptSegment],
        translated_texts: List[str],
        output_path: Path
    ) -> Path:
        """
        توليد ملف SRT بالترجمة مع الحفاظ على الطوابع الزمنية الأصلية.
        
        Args:
            original_segments: المقاطع الأصلية مع الطوابع الزمنية
            translated_texts: النصوص المترجمة بنفس الترتيب
            output_path: مسار الملف الناتج
        """
        if len(original_segments) != len(translated_texts):
            logger.warning(
                f"عدم تطابق: {len(original_segments)} مقطع، {len(translated_texts)} ترجمة"
            )
            min_len = min(len(original_segments), len(translated_texts))
            original_segments = original_segments[:min_len]
            translated_texts = translated_texts[:min_len]

        merged_segments = []
        for seg, translated in zip(original_segments, translated_texts):
            merged_segments.append(TranscriptSegment(
                start=seg.start, end=seg.end, text=translated
            ))

        return SRTGenerator.generate(merged_segments, output_path)

    @staticmethod
    def export_txt(segments: List[TranscriptSegment], output_path: Path) -> Path:
        """تصدير نص كامل بدون طوابع زمنية بصيغة TXT."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        text = "\n".join(seg.text for seg in segments)
        text += CONFIG.get_footer()
        output_path.write_text(text, encoding="utf-8")
        return output_path

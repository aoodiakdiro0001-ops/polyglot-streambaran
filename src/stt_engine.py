"""
============================================================
 طبقة التفريغ الصوتي (Speech-to-Text Engine Layer)
 المؤلف: Baran Avisat  |  Baranavisat@gmail.com
============================================================
 تستخدم نموذج Whisper مفتوح المصدر لتحويل الصوت إلى نص
 دقيق مع طوابع زمنية، عبر Hugging Face Inference API مجاناً.
"""

import os
import json
import logging
import requests
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from config import CONFIG

logger = logging.getLogger(__name__)


@dataclass
class TranscriptSegment:
    """مقطع نصي مع طابع زمني."""
    start: float       # بالثواني
    end: float         # بالثواني
    text: str
    confidence: float = 1.0

    def to_srt_block(self, index: int) -> str:
        """تحويل المقطع إلى كتلة SRT."""
        return f"{index}\n{self._format_time(self.start)} --> {self._format_time(self.end)}\n{self.text.strip()}\n"

    @staticmethod
    def _format_time(seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


class STTEngine:
    """محرّك تحويل الصوت إلى نص باستخدام Whisper."""

    def __init__(self, use_hf_api: bool = True):
        self.use_hf_api = use_hf_api
        self.hf_token = CONFIG.KEYS.huggingface
        self.model_name = CONFIG.MODELS.hf_whisper_model
        self.local_model = None
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model_name}"

    # --------------------------------------------------------
    # تهيئة نموذج Whisper محلي (يفضّل في حالة التشغيل على HF Spaces)
    # --------------------------------------------------------
    def _init_local_model(self):
        if self.local_model is not None:
            return
        logger.info(f"تحميل نموذج Whisper المحلي: {CONFIG.MODELS.whisper_model}")
        try:
            import whisper
            self.local_model = whisper.load_model(CONFIG.MODELS.whisper_model)
        except ImportError:
            logger.warning("مكتبة whisper غير مثبتة. سيتم استخدام HF API.")
            self.use_hf_api = True

    # --------------------------------------------------------
    # التفريغ عبر Hugging Face Inference API (مجاني 100%)
    # --------------------------------------------------------
    def transcribe_via_hf_api(self, audio_path: Path) -> dict:
        """يرسل الصوت إلى Hugging Face Inference API للتفريغ."""
        if not self.hf_token:
            raise ValueError("HF_TOKEN مطلوب لاستخدام Hugging Face API")

        audio_path = Path(audio_path)
        with open(audio_path, "rb") as f:
            audio_bytes = f.read()

        headers = {"Authorization": f"Bearer {self.hf_token}"}
        logger.info(f"إرسال الصوت إلى HF API: {self.model_name}")

        response = requests.post(
            self.api_url, headers=headers, data=audio_bytes, timeout=300
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"فشل HF API ({response.status_code}): {response.text}"
            )

        return response.json()

    # --------------------------------------------------------
    # التفريغ عبر نموذج Whisper المحلي
    # --------------------------------------------------------
    def transcribe_locally(self, audio_path: Path, language: Optional[str] = None) -> dict:
        """يستخدم نموذج Whisper المحلي للتفريغ مع الطوابع الزمنية."""
        self._init_local_model()
        if self.local_model is None:
            raise RuntimeError("تعذر تحميل نموذج Whisper المحلي")

        logger.info(f"بدء التفريغ المحلي: {audio_path.name}")
        options = {"word_timestamps": True, "verbose": False}
        if language:
            options["language"] = language

        result = self.local_model.transcribe(str(audio_path), **options)
        return result

    # --------------------------------------------------------
    # الواجهة الموحدة للتفريغ
    # --------------------------------------------------------
    def transcribe(self, audio_path: Path, language: Optional[str] = None) -> list:
        """
        الواجهة الموحدة لتفريغ الصوت.
        
        Returns:
            قائمة بكائنات TranscriptSegment
        """
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"ملف الصوت غير موجود: {audio_path}")

        if self.use_hf_api and self.hf_token:
            raw = self.transcribe_via_hf_api(audio_path)
        else:
            raw = self.transcribe_locally(audio_path, language)

        segments = self._parse_result(raw)
        logger.info(f"تم تفريغ {len(segments)} مقطع صوتي")
        return segments

    # --------------------------------------------------------
    # تحويل النتيجة الخام إلى مقاطع منظمة
    # --------------------------------------------------------
    def _parse_result(self, raw: dict) -> list:
        """يحوّل مخرجات Whisper إلى قائمة TranscriptSegment."""
        segments = []
        for seg in raw.get("segments", []):
            text = seg.get("text", "").strip()
            if not text:
                continue
            segments.append(TranscriptSegment(
                start=float(seg.get("start", 0)),
                end=float(seg.get("end", 0)),
                text=text,
                confidence=float(seg.get("avg_logprob", 0))
            ))

        # إذا لم توجد مقاطع، استخدم النص الكامل كقطعة واحدة
        if not segments and raw.get("text"):
            segments.append(TranscriptSegment(
                start=0.0, end=0.0, text=raw["text"].strip()
            ))
        return segments

    # --------------------------------------------------------
    # تصدير النص الكامل
    # --------------------------------------------------------
    @staticmethod
    def segments_to_text(segments: list) -> str:
        """دمج كل المقاطع في نص متصل."""
        return "\n".join(seg.text for seg in segments)

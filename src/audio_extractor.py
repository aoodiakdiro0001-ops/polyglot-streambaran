"""
============================================================
 طبقة استخراج الصوت من الفيديو (Audio Extractor Layer)
 المؤلف: Baran Avisat  |  Baranavisat@gmail.com
============================================================
 تستخرج المسار الصوتي من روابط يوتيوب أو ملفات الفيديو
 المحلية وتحوله إلى صيغة WAV مناسب لنموذج Whisper.
"""

import os
import subprocess
import logging
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import yt_dlp
from pydub import AudioSegment

from config import CONFIG

logger = logging.getLogger(__name__)


class AudioExtractor:
    """استخراج الصوت من أي مصدر مدعوم."""

    SUPPORTED_VIDEO_FORMATS = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".flv", ".wmv"}
    SUPPORTED_AUDIO_FORMATS = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac"}

    def __init__(self):
        self.temp_dir = CONFIG.PATHS.temp_dir
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------------
    # استخراج صوت من رابط يوتيوب أو أي منصات مدعومة
    # --------------------------------------------------------
    def extract_from_url(self, url: str, output_name: Optional[str] = None) -> Path:
        """
        يستخرج الصوت من رابط فيديو ويحوله إلى WAV.
        
        Args:
            url: رابط الفيديو (يوتيوب، فيسبوك، تويتر، إلخ)
            output_name: اسم الملف الناتج (اختياري)
        
        Returns:
            مسار ملف الصوت المستخرج بصيغة WAV
        """
        if not self._is_valid_url(url):
            raise ValueError(f"الرابط غير صالح: {url}")

        output_name = output_name or "audio_extract"
        output_template = str(self.temp_dir / f"{output_name}.%(ext)s")
        final_wav = self.temp_dir / f"{output_name}.wav"

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": output_template,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }],
            "quiet": True,
            "no_warnings": True,
        }

        logger.info(f"بدء استخراج الصوت من: {url}")
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            logger.error(f"فشل استخراج الصوت: {e}")
            raise RuntimeError(f"تعذر استخراج الصوت من الرابط: {e}")

        if not final_wav.exists():
            raise FileNotFoundError(f"لم يتم إنشاء ملف الصوت: {final_wav}")

        logger.info(f"تم استخراج الصوت بنجاح: {final_wav}")
        return final_wav

    # --------------------------------------------------------
    # استخراج صوت من ملف فيديو محلي
    # --------------------------------------------------------
    def extract_from_file(self, video_path: Path) -> Path:
        """يستخرج المسار الصوتي من ملف فيديو محلي."""
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"الملف غير موجود: {video_path}")

        ext = video_path.suffix.lower()
        if ext in self.SUPPORTED_AUDIO_FORMATS:
            # الملف أصلاً صوتي — حوّله إلى WAV موحد
            return self._convert_to_wav(video_path)

        if ext not in self.SUPPORTED_VIDEO_FORMATS:
            raise ValueError(f"صيغة غير مدعومة: {ext}")

        output_wav = self.temp_dir / f"{video_path.stem}_audio.wav"
        cmd = [
            "ffmpeg", "-y", "-i", str(video_path),
            "-vn", "-acodec", "pcm_s16le",
            "-ar", "16000", "-ac", "1",
            str(output_wav)
        ]
        logger.info(f"استخراج الصوت من: {video_path.name}")
        subprocess.run(cmd, check=True, capture_output=True)
        return output_wav

    # --------------------------------------------------------
    # تحويل أي صيغة صوتية إلى WAV موحد 16kHz مونو
    # --------------------------------------------------------
    def _convert_to_wav(self, audio_path: Path) -> Path:
        output_wav = self.temp_dir / f"{audio_path.stem}_converted.wav"
        audio = AudioSegment.from_file(audio_path)
        audio = audio.set_frame_rate(16000).set_channels(1)
        audio.export(output_wav, format="wav")
        return output_wav

    # --------------------------------------------------------
    # التحقق من صحة الرابط
    # --------------------------------------------------------
    @staticmethod
    def _is_valid_url(url: str) -> bool:
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    # --------------------------------------------------------
    # تقسيم الصوت الطويل إلى مقاطع صغيرة للمعالجة
    # --------------------------------------------------------
    def split_audio(self, audio_path: Path, segment_minutes: int = 30) -> list:
        """يقسّم الملف الصوتي الطويل إلى مقاطع لمعالجة أسهل."""
        audio_path = Path(audio_path)
        audio = AudioSegment.from_file(audio_path)
        segment_ms = segment_minutes * 60 * 1000
        segments = []

        total_segments = (len(audio) // segment_ms) + 1
        for i in range(total_segments):
            start = i * segment_ms
            end = min((i + 1) * segment_ms, len(audio))
            if start >= len(audio):
                break
            segment = audio[start:end]
            seg_path = self.temp_dir / f"{audio_path.stem}_part_{i:03d}.wav"
            segment.export(seg_path, format="wav")
            segments.append(seg_path)

        logger.info(f"تم تقسيم الصوت إلى {len(segments)} مقطع")
        return segments

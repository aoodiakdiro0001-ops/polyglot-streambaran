"""
============================================================
 حزمة المصادر الرئيسية (src package)
 المؤلف: Baran Avisat  |  Baranavisat@gmail.com
============================================================
"""

from .audio_extractor import AudioExtractor
from .stt_engine import STTEngine, TranscriptSegment
from .translator import AITranslator
from .database import DatabaseManager, ProcessRecord
from .srt_generator import SRTGenerator

__all__ = [
    "AudioExtractor",
    "STTEngine",
    "TranscriptSegment",
    "AITranslator",
    "DatabaseManager",
    "ProcessRecord",
    "SRTGenerator",
]

__author__ = "Baran Avisat"
__email__ = "Baranavisat@gmail.com"
__version__ = "1.0.0"

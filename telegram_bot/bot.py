"""
============================================================
 بوت تليجرام (Telegram Bot) - طبقة التسليم
 المؤلف: Baran Avisat  |  Baranavisat@gmail.com
============================================================
 يستقبل روابط الفيديو أو الملفات الصوتية عبر تليجرام،
 يعالجها بالكامل، ويرسل ملفات SRT و TXT والملخص فوراً.
"""

import os
import logging
import asyncio
from pathlib import Path

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters,
)

from config import CONFIG
from main import PipelineOrchestrator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


class PolyGlotTelegramBot:
    """بوت تليجرام للمنظومة الكاملة."""

    SUPPORTED_LANGS = {
        "🇸🇦 عربي": "ar", "🇬🇧 إنجليزي": "en", "🇹🇷 تركي": "tr",
        "🇫🇷 فرنسي": "fr", "🇩🇪 ألماني": "de", "🇪🇸 إسباني": "es",
        "🇮🇹 إيطالي": "it", "🇷🇺 روسي": "ru", "🇨🇳 صيني": "zh",
        "🇯🇵 ياباني": "ja", "🇰🇷 كوري": "ko", "🇮🇷 فارسي": "fa",
    }

    def __init__(self):
        self.pipeline = None
        self.user_states = {}  # تتبع لغة كل مستخدم

    def _ensure_pipeline(self):
        if self.pipeline is None:
            provider = "gemini" if CONFIG.KEYS.gemini else "groq"
            self.pipeline = PipelineOrchestrator(ai_provider=provider)

    # --------------------------------------------------------
    # الأمر /start
    # --------------------------------------------------------
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        welcome = (
            f"🌟 مرحباً بك في **{CONFIG.PROJECT_NAME}** 🌟\n\n"
            f"المنظومة الذاتية للترجمة، تفريغ الصوت، وتوليد الترجمات المرئية.\n\n"
            f"📋 **طريقة الاستخدام:**\n"
            f"1️⃣ اختر لغة الترجمة المرغوبة بالأمر /lang\n"
            f"2️⃣ أرسل رابط فيديو (يوتيوب وغيرها) أو ملفاً صوتياً/فيديو\n"
            f"3️⃣ انتظر دقائق وستصلك ملفات SRT + TXT + الملخص\n\n"
            f"🔧 **الأوامر المتاحة:**\n"
            f"/start - بدء التشغيل\n"
            f"/lang - اختيار لغة الترجمة\n"
            f"/help - المساعدة\n"
            f"/about - عن المشروع\n\n"
            f"👤 **المؤلف:** {CONFIG.AUTHOR_NAME}\n"
            f"📧 {CONFIG.AUTHOR_EMAIL}\n"
            f"📱 واتساب: {CONFIG.AUTHOR_WHATSAPP}"
        )
        await update.message.reply_text(welcome, parse_mode="Markdown")

    # --------------------------------------------------------
    # الأمر /lang - اختيار اللغة
    # --------------------------------------------------------
    async def lang_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = []
        for name, code in self.SUPPORTED_LANGS.items():
            keyboard.append([InlineKeyboardButton(name, callback_data=f"lang_{code}")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🌍 اختر لغة الترجمة المرغوبة:", reply_markup=reply_markup
        )

    async def lang_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        code = query.data.replace("lang_", "")
        self.user_states[query.from_user.id] = {"lang": code}
        lang_name = next((n for n, c in self.SUPPORTED_LANGS.items() if c == code), code)
        await query.edit_message_text(f"✅ تم اختيار اللغة: **{lang_name}**\n\nالآن أرسل رابطاً أو ملفاً للبدء.", parse_mode="Markdown")

    # --------------------------------------------------------
    # معالجة الروابط
    # --------------------------------------------------------
    async def handle_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        url = update.message.text.strip()
        user_id = update.effective_user.id
        target_lang = self.user_states.get(user_id, {}).get("lang", "ar")

        await update.message.reply_text(
            f"⏳ جارٍ المعالجة...\n🔗 الرابط: {url}\n🌍 اللغة: {target_lang}\n\nقد يستغرق ذلك عدة دقائق حسب طول الفيديو."
        )

        try:
            self._ensure_pipeline()
            result = self.pipeline.process_url(url, target_lang=target_lang)

            # إرسال الملفات
            await self._send_results(update, result)
        except Exception as e:
            logger.error(f"خطأ في المعالجة: {e}", exc_info=True)
            await update.message.reply_text(
                f"❌ حدث خطأ أثناء المعالجة: {str(e)}\n\n"
                f"للدعم تواصل مع: {CONFIG.AUTHOR_EMAIL}"
            )

    # --------------------------------------------------------
    # معالجة الملفات الصوتية/المرئية المرسلة
    # --------------------------------------------------------
    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        doc = update.message.document
        if not doc:
            return

        user_id = update.effective_user.id
        target_lang = self.user_states.get(user_id, {}).get("lang", "ar")

        await update.message.reply_text(
            f"📥 تم استلام الملف: {doc.file_name}\n⏳ جارٍ المعالجة باللغة: {target_lang}"
        )

        try:
            # تنزيل الملف
            file = await doc.get_file()
            local_path = CONFIG.PATHS.temp_dir / doc.file_name
            await file.download_to_drive(custom_path=str(local_path))

            self._ensure_pipeline()
            result = self.pipeline.process_file(local_path, target_lang=target_lang)
            await self._send_results(update, result)

            # تنظيف
            local_path.unlink(missing_ok=True)
        except Exception as e:
            logger.error(f"خطأ في معالجة الملف: {e}", exc_info=True)
            await update.message.reply_text(f"❌ خطأ: {str(e)}")

    # --------------------------------------------------------
    # إرسال النتائج للمستخدم
    # --------------------------------------------------------
    async def _send_results(self, update: Update, result: dict):
        # إرسال ملف SRT
        srt_path = Path(result["srt_path"])
        if srt_path.exists():
            with open(srt_path, "rb") as f:
                await update.message.reply_document(
                    document=f, filename=srt_path.name,
                    caption="🎬 ملف الترجمة (SRT) جاهز للعرض"
                )

        # إرسال ملف TXT
        txt_path = Path(result["txt_path"])
        if txt_path.exists():
            with open(txt_path, "rb") as f:
                await update.message.reply_document(
                    document=f, filename=txt_path.name,
                    caption="📄 النص المترجم الكامل (TXT)"
                )

        # إرسال الملخص
        if result.get("summary"):
            summary_text = (
                f"📝 **الملخص التنفيذي:**\n\n{result['summary']}\n\n"
                f"⏱️ المدة: {result['duration_seconds']:.1f} ثانية\n"
                f"🔢 عدد المقاطع: {result['segments_count']}"
            )
            await update.message.reply_text(summary_text, parse_mode="Markdown")

        await update.message.reply_text(
            f"✅ تمت المعالجة بنجاح!\n\n👤 {CONFIG.AUTHOR_NAME}\n📧 {CONFIG.AUTHOR_EMAIL}\n📱 {CONFIG.AUTHOR_WHATSAPP}"
        )

    # --------------------------------------------------------
    # الأوامر المساعدة
    # --------------------------------------------------------
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "🔧 **المساعدة:**\n\n"
            "1. استخدم /lang لاختيار لغة الترجمة\n"
            "2. أرسل رابط فيديو أو ملفاً صوتياً\n"
            "3. ستصلك النتائج خلال دقائق\n\n"
            "اللغات المدعومة: عربي، إنجليزي، تركي، فرنسي، ألماني، إسباني، "
            "إيطالي، روسي، صيني، ياباني، كوري، فارسي.",
            parse_mode="Markdown",
        )

    async def about_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            f"🚀 **{CONFIG.PROJECT_NAME}** v{CONFIG.PROJECT_VERSION}\n\n"
            f"المنظومة الذاتية للترجمة، تفريغ الصوت، وتوليد الترجمات المرئية.\n\n"
            f"✨ **المزايا:**\n"
            f"• تفريغ صوتي دقيق بطوابع زمنية\n"
            f"• ترجمة ذكية لأكثر من 12 لغة\n"
            f"• تلخيص تنفيذي تلقائي\n"
            f"• تصدير SRT و TXT\n"
            f"• 100% موارد مجانية\n\n"
            f"👤 **المؤلف:** {CONFIG.AUTHOR_NAME}\n"
            f"📧 {CONFIG.AUTHOR_EMAIL}\n"
            f"📱 واتساب: {CONFIG.AUTHOR_WHATSAPP}\n\n"
            f"{CONFIG.COPYRIGHT_NOTICE}",
            parse_mode="Markdown",
        )

    # --------------------------------------------------------
    # تشغيل البوت
    # --------------------------------------------------------
    def run(self):
        token = CONFIG.KEYS.telegram_bot
        if not token:
            raise ValueError("TELEGRAM_BOT_TOKEN مطلوب. ضعه في ملف .env")

        app = Application.builder().token(token).build()
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("lang", self.lang_command))
        app.add_handler(CommandHandler("help", self.help_command))
        app.add_handler(CommandHandler("about", self.about_command))
        app.add_handler(CallbackQueryHandler(self.lang_callback))
        app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^https?://"), self.handle_url))
        app.add_handler(MessageHandler(filters.Document.ALL, self.handle_document))

        logger.info(f"🚀 تشغيل بوت {CONFIG.PROJECT_NAME}...")
        app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    bot = PolyGlotTelegramBot()
    bot.run()

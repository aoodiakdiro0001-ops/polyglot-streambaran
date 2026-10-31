# ============================================================
# PolyGlot-StreamBaran - Dockerfile
# المؤلف: Baran Avisat | Baranavisat@gmail.com
# ============================================================
# صورة Docker جاهزة لتشغيل المنظومة في أي بيئة
# ============================================================

FROM python:3.11-slim

# معلومات المؤلف
LABEL author="Baran Avisat"
LABEL email="Baranavisat@gmail.com"
LABEL version="1.0.0"
LABEL description="PolyGlot-StreamBaran - Autonomous Translation & Transcription System"

# تثبيت متطلبات النظام
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# مجلد العمل
WORKDIR /app

# نسخ المتطلبات وتثبيتها
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# نسخ باقي الملفات
COPY . .

# إنشاء المجلدات المطلوبة
RUN mkdir -p temp output logs

# المنفذ الافتراضي لواجهة Streamlit
EXPOSE 8501

# متغيرات البيئة الافتراضية
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# نقطة الدخول الافتراضية (يمكن تغييرها)
CMD ["streamlit", "run", "web_dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0"]

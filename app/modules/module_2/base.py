"""
Video Modülü - Base Class
=========================

Bu dosyada tüm video tiplerinin türeyeceği abstract base class tanımlanmıştır.
Ortak özellikler burada tutulur.
Exception sınıfları ve yardımcı fonksiyonlar da bu dosyada yer alır.
"""

from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid
import re

class VideoError(Exception):
    """Tüm video ile ilgili hatalar için temel sınıf."""
    def __init__(self, message: str = "Belirtilmeyen bir video hatası oluştu."):
        self.message = message
        super().__init__(self.message)

class VideoNotFoundError(VideoError):
    """Video deposunda video bulunamadığında hata verir."""
    def __init__(self, video_id: str):
        self.video_id = video_id
        super().__init__(f"'{video_id}' ID'li video bulunamadı.")


class VideoValidationError(VideoError):
    """Video veri doğrulama başarısız olduğunda hata verir"""
    pass

class InvalidVideoStatusError(VideoError):
    """Geçersiz bir durum geçişi denendiğinde hata verir"""
    def __init__(self, current_status: str, target_status: str, video_id: str):
        self.current_status = current_status
        self.target_status = target_status
        self.video_id = video_id
        super().__init__(
            f"'{video_id}' videosu için '{current_status}' durumundan '{target_status}' "
            f"durumuna geçiş geçersizdir."
        )

class InvalidVisibilityError(VideoError):
    """Geçersiz bir görünürlük ayarı sağlandığında hata verir."""
    pass

class VideoUploadError(VideoError):
    """Video yükleme simülasyonu sırasında bir hata oluştuğunda hata verir."""
    pass

class VideoProcessingError(VideoError):
    """Video işleme sırasında bir hata oluştuğunda hata verirr."""
    pass

class RepositoryError(VideoError):
    """Bir depo (repository) işlemi başarısız olduğunda hata verir."""
    pass

class VideoVisibility(Enum):

    PUBLIC = "public"      # Herkese açık
    PRIVATE = "private"    # Sadece bana özel
    UNLISTED = "unlisted"  # Linki olan görebilir

class VideoStatus(Enum):

    UPLOADED = "uploaded"     # Yüklendi
    PROCESSING = "processing" # İşleniyor
    PUBLISHED = "published"   # Yayında
    BLOCKED = "blocked"       # Yasaklı
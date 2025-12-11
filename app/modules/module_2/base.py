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

# VideoBase Class

class VideoBase(ABC):
    """
    Tüm videolar için temel sınıf.
    Her video tipinde olması gereken ortak özellikleri ve mecburi metotları barındırır.
    """
    def __init__(
        self,
        channel_id: str,
        title: str,
        description: str,
        duration_seconds: int,
        visibility: VideoVisibility = VideoVisibility.PRIVATE,
        tags: Optional[List[str]] = None
    ):
        # Unique ID oluştma
        self._video_id = str(uuid.uuid4())
        self._channel_id = channel_id
        
        # Setter'ları kullanarak atama yapma
        self.title = title 
        self._description = description
        
        self._duration_seconds = duration_seconds
        self._visibility = visibility
        self._status = VideoStatus.UPLOADED
        
        # Tarih bilgileri
        self._created_at = datetime.now()
        self._published_at: Optional[datetime] = None
        
        self._tags = tags if tags else []
        
        # İstatistikler (default 0)
        self._view_count = 0
        self._likes = 0

    # --- Property Tanımları ---

    @property
    def video_id(self) -> str:
        return self._video_id

    @property
    def channel_id(self) -> str:
        return self._channel_id

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, new_title: str):
        # Başlık kotrolü
        if not new_title:
            raise ValueError("Başlık boş bırakılamaz.")
        self._title = new_title

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, new_description: str):
        self._description = new_description

    @property
    def duration_seconds(self) -> int:
        return self._duration_seconds

    @property
    def visibility(self) -> VideoVisibility:
        return self._visibility

    @visibility.setter
    def visibility(self, new_visibility: VideoVisibility):
        # Tip kontrolü yapma
        if not isinstance(new_visibility, VideoVisibility):
            raise InvalidVisibilityError(f"Hatalı görünürlük tipi: {new_visibility}")
        self._visibility = new_visibility

    @property
    def status(self) -> VideoStatus:
        return self._status
    
    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def published_at(self) -> Optional[datetime]:
        return self._published_at

    @property
    def tags(self) -> List[str]:
        return self._tags

    # --- Metotlar ---

    def add_tag(self, tag: str):
        """Etiket ekler (tekrarı önler)."""
        if tag not in self._tags:
            self._tags.append(tag)

    def remove_tag(self, tag: str):
        """Varsa etiketi siler."""
        if tag in self._tags:
            self._tags.remove(tag)

    @abstractmethod
    def get_video_type(self) -> str:
        """Video tipini string olarak döner"""
        pass

    @abstractmethod
    def calculate_monetization_potential(self) -> float:
        """Tahmini gelir potansiyelini hesaplar."""
        pass
    
    @abstractmethod
    def validate_content_policy(self) -> bool:
        """İçerik kurallarına uygun mu diye bakar."""
        pass
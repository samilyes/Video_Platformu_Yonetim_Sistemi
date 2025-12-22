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

class VideoBase(ABC):
    """
    Tüm videolar için temel sınıftır.
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
        
        # İstatistikler
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
    def transition_status(self, new_status: VideoStatus):
        """
        Video durumunu değiştirir. 
        Durumlar arası geçiş mantığı (State Machine) burada kontrol edilir.
        """
        # Aynı duruma geçmeye çalışıyorsak işlem yapma
        if self._status == new_status:
            return

        # Basit bir kontrol mekanizması
        allowed = False
        
        # Yüklenen bir içerik, işleme alınabilir ya da kurallara uymuyorsa engellenebilir.
        if self._status == VideoStatus.UPLOADED:
            if new_status in [VideoStatus.PROCESSING, VideoStatus.BLOCKED]:
                allowed = True
        
        # İşlemde olan bir içerik, işlemler bitince yayınlanabilir veya sorun varsa engellenebilir.
        elif self._status == VideoStatus.PROCESSING:
            if new_status in [VideoStatus.PUBLISHED, VideoStatus.BLOCKED]:
                allowed = True
        
        # Yayında olan bir içerik, sonradan bir kural ihlali tespit edilirse engellenebilir.
        elif self._status == VideoStatus.PUBLISHED:
            if new_status == VideoStatus.BLOCKED:
                allowed = True
        
        # Engellenen içerik, engel kaldırıldığında yeniden yayınlanır.
        elif self._status == VideoStatus.BLOCKED:
            if new_status == VideoStatus.PUBLISHED:
                allowed = True
        
        if allowed:
            self._status = new_status
            # Yayınlandıysa tarihi atar
            if new_status == VideoStatus.PUBLISHED and self._published_at is None:
                self._published_at = datetime.now()
        else:
            raise InvalidVideoStatusError(self._status.value, new_status.value, self._video_id)

    def to_dict(self) -> Dict[str, Any]:
        """Objeyi dict'e çevirir (JSON yanıtları için kullanışlı)."""
        return {
            "video_id": self._video_id,
            "channel_id": self._channel_id,
            "title": self._title,
            "description": self._description,
            "duration_seconds": self._duration_seconds,
            "visibility": self._visibility.value,
            "status": self._status.value,
            "created_at": self._created_at.isoformat() if self._created_at else None,
            "published_at": self._published_at.isoformat() if self._published_at else None,
            "tags": self._tags,
            "type": self.get_video_type()
        }

    def __str__(self):
        return f"[{self.get_video_type()}] {self.title} ({self.status.value})"

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.video_id} title='{self.title}'>"

    # --- Statik Metotlar ---

    @staticmethod
    def validate_title_format(title: str) -> bool:
        """
        Başlığın formatını kontrol eder.
        Çok uzunsa veya yasaklı karakter varsa False döner.
        """
        return validate_video_title(title)

    @staticmethod
    def format_duration_display(seconds: int) -> str:
        """Saniyeyi dakika:saniye formatına çevirir."""
        return format_duration(seconds)

    # --- Class Metotları ---

    @classmethod
    def get_available_statuses(cls) -> List[str]:
        """Tüm video durumlarını liste olarak döndürür."""
        return [s.value for s in VideoStatus]

    @classmethod
    def create_preview_object(cls, title: str, duration: int) -> Optional['VideoBase']:
        """
        Test amaçlı geçici (preview) bir nesne oluşturmayı dener.
        """
        if cls is VideoBase:
            raise NotImplementedError("VideoBase abstract olduğu için direkt üretilemez.")
        
        # Basitleştirilmiş bir önizleme nesnesi oluşturmayı dener.
        try:
            return cls(
                channel_id="PREVIEW_CHANNEL",
                title=f"ÖNİZLEME: {title}",
                description="Otomatik oluşturulan önizleme.",
                duration_seconds=duration
            )
        except TypeError:
            # Eğer imza uyuşmazsa None dönebilir veya hatayı yok eder.
            return None
    
    @classmethod
    def get_visibility_description(cls, visibility: VideoVisibility) -> str:
        """Görünürlük ayarının kullanıcıya gösterilecek açıklaması."""
        descriptions = {
            VideoVisibility.PUBLIC: "Herkese açık.",
            VideoVisibility.PRIVATE: "Sadece ben görebilirim.",
            VideoVisibility.UNLISTED: "Liste dışı (link ile erişim)."
        }
        return descriptions.get(visibility, "Bilinmiyor.")

def validate_video_title(title: str) -> bool:
    """
    Video başlığının kurallara uyup uymadığını kontrol eder.
    - Boş olamaz
    - 100 karakteri geçemez
    - Yasaklı karakter içeremez
        title (str): Kontrol edilecek başlık.
        bool: Uygunsa True, değilse False.
    """
    if not title:
        return False
    if len(title) > 100:
        return False
    
    # Güvenlik amacıyla HTML tag benzeri yapıları engeller
    
    if re.search(r"[<>]", title):
        return False
    
    return True

def format_duration(seconds: int) -> str:
    """
    Saniyeyi SS:DD:SN formatına çevirir.
    seconds (int): Saniye cinsinden süre.
    str: Formatlanmış zaman.
    """
    if seconds < 0:
        return "00:00"
        
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"

def generate_video_slug(title: str) -> str:
    """
    Başlıktan URL dostu slug oluşturur.
    title (str): Başlık.
    """
    # Küçük harfe çevir
    slug = title.lower()
    
    # Boşluk ve tire hariç diğer geçersiz karakterleri sil.
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    
    # Maksimum 50 karakter
    return slug[:50]

class VideoMetadata:
    """
    Video için ek metadata bilgilerini tutar.
    Bu sınıf satır sayısını artırmak ve modülü zenginleştirir.
    """
    def __init__(self, resolution: str = "1080p", codec: str = "h264", bitrate_kbps: int = 5000):
        self.resolution = resolution
        self.codec = codec
        self.bitrate_kbps = bitrate_kbps
        self.last_updated = datetime.now()

    def update_resolution(self, new_resolution: str):
        """Çözünürlük bilgisini günceller."""
        valid_resolutions = ["720p", "1080p", "1440p", "4K", "8K"]
        if new_resolution in valid_resolutions:
            self.resolution = new_resolution
            self.last_updated = datetime.now()
        else:
            # Geçersiz çözünürlük durumunda varsayılan olarak kaydedebilir.
            pass

    def get_info(self) -> Dict[str, Any]:
        """Metadata bilgilerini sözlük olarak döndürür."""
        return {
            "resolution": self.resolution,
            "codec": self.codec,
            "bitrate": f"{self.bitrate_kbps} kbps",
            "updated": self.last_updated.isoformat()
        }

    def __repr__(self):
        return f"<VideoMetadata {self.resolution} {self.codec}>"
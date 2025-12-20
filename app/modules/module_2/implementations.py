"""
Video Uygulamaları ve Servisleri (Implementations)
==================================================

Bu modül, `VideoBase` soyut sınıfının somut uygulamalarını (Entities)
ve video iş mantığını yöneten servis sınıfını (Service Layer) içerir.

Bu dosya şunları içerir:
1. Video Entities (Entities/Models): StandardVideo, LiveStreamVideo, ShortVideo
2. Video Service (Service Layer): VideoService
"""

import time
import logging
import random
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from .base import (
    VideoBase, VideoVisibility, VideoStatus, 
    VideoUploadError, VideoProcessingError, InvalidVideoStatusError,
    VideoMetadata
)
from .repository import VideoRepository
from app.modules.module_1.implementations import KidsChannel
# Logger ayarı
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("VideoModule")

# Video Entities (Modeller)

class StandardVideo(VideoBase):
    """
    Standart yüklenen video.
    Genelde 1080p, 4K gibi çözünürlükleri olur ve reklam geliri modeli buna göre çalışır.
    
    Özellikler:
    - resolution: Video çözünürlüğü.
    - has_subtitles: Altyazı desteği.
    - allow_comments: Yorumlara izin verme.
    """

    def __init__(
        self,
        channel_id: str,
        title: str,
        description: str,
        duration_seconds: int,
        visibility: VideoVisibility = VideoVisibility.PRIVATE,
        tags: Optional[List[str]] = None,
        resolution: str = "1080p",
        has_subtitles: bool = False,
        allow_comments: bool = True
    ):
        super().__init__(channel_id, title, description, duration_seconds, visibility, tags)
        self.resolution = resolution
        self.has_subtitles = has_subtitles
        self.allow_comments = allow_comments
        
        # Metadata nesnesini de başlatma
        self.metadata = VideoMetadata(resolution=resolution)

    def get_video_type(self) -> str:
        return "StandardVideo"

    def calculate_monetization_potential(self) -> float:
        """
        Gelir potansiyeli hesaplama.
        10 dakikadan uzunsa daha çok reklam koyulabilir ve puan artar.
        """
        base_score = 1.0
        
        # 10 dakika (600 sn) kontrolü
        if self.duration_seconds > 600:
            base_score += 0.5
        elif self.duration_seconds < 60:
            base_score -= 0.2 # Çok kısaysa az gelir
            
        # Çözünürlük etkisi
        if self.resolution in ["4K", "8K"]:
            base_score += 0.3
        elif self.resolution == "720p":
            base_score -= 0.1
            
        return max(0.0, base_score)

    def validate_content_policy(self) -> bool:
        """
        Standart video kuralları:
        - Başlık çok uzun olmamalı.
        - Açıklama mutlaka olmalı.
        - En az 5 saniye olmalı.
        """
        if len(self.title) > 100:
            return False
        if not self.description:
            return False # Açıklamasız video olmaz
        if self.duration_seconds < 5:
            return False
        return True
        
    def set_resolution(self, resolution: str):
        self.resolution = resolution
        self.metadata.update_resolution(resolution)

    def toggle_comments(self):
        """Yorumları aç/kapa."""
        self.allow_comments = not self.allow_comments


class LiveStreamVideo(VideoBase):
    """
    Canlı yayın nesnesi.
    Normal videodan farkı, başta süresinin belli olmaması ve 'schedule' edilebilmesi.
    """

    def __init__(
        self,
        channel_id: str,
        title: str,
        description: str,
        visibility: VideoVisibility = VideoVisibility.PUBLIC,
        tags: Optional[List[str]] = None,
        scheduled_start_time: Optional[datetime] = None,
        chat_enabled: bool = True
    ):
        # Canlı yayın başta 0 saniyedir.
        super().__init__(channel_id, title, description, 0, visibility, tags)
        self.scheduled_start_time = scheduled_start_time
        self.is_live = False
        self.chat_enabled = chat_enabled
        self.max_concurrent_viewers = 0

    def get_video_type(self) -> str:
        return "LiveStreamVideo"

    def calculate_monetization_potential(self) -> float:
        # Canlı yayınlarda bağış toplama ihtimali yüksek
        base_score = 1.5 
        if self.chat_enabled:
            base_score += 0.5
        if self.scheduled_start_time:
            base_score += 0.2 # Önceden haber verilmişse daha iyi
        return base_score

    def validate_content_policy(self) -> bool:
        # Sadece başlık olsa yeterli şimdilik
        if not self.title:
            return False
        return True

    def transition_status(self, new_status: VideoStatus):
        """
        Override: Canlı yayınlar direkt 'Yayında' (PUBLISHED) durumuna geçebilir.
        Processing aşamasını atlayabilirler (gerçek zamanlı işleme).
        """
        # Uploaded -> Published geçişine izin ver
        if self._status == VideoStatus.UPLOADED and new_status == VideoStatus.PUBLISHED:
            self._status = new_status
            if self._published_at is None:
                self._published_at = datetime.now()
            return

        # Diğer durumlar için normal akış devam etsin
        super().transition_status(new_status)

    def start_stream(self):
        """Yayını başlatır."""
        self.is_live = True
        self.transition_status(VideoStatus.PUBLISHED)
    
    def end_stream(self, duration_seconds: int):
        """Yayını bitirir ve toplam süreyi kaydeder."""
        self.is_live = False
        self._duration_seconds = duration_seconds
        # TODO: Burada VOD (tekrar izleme) kaydı oluşturulabilir.


class ShortVideo(VideoBase):
    """
    Shorts / Reels tarzı dikey videolar.
    Süre kısıtlaması vardır (<60 sn).
    """

    def __init__(
        self,
        channel_id: str,
        title: str,
        description: str,
        duration_seconds: int,
        visibility: VideoVisibility = VideoVisibility.PUBLIC,
        tags: Optional[List[str]] = None,
        music_track_id: Optional[str] = None,
        filter_used: Optional[str] = None
    ):
        super().__init__(channel_id, title, description, duration_seconds, visibility, tags)
        self.music_track_id = music_track_id
        self.filter_used = filter_used
        # En boy oranı sabit 9:16 olarak ayarlanSIN
        self.aspect_ratio = "9:16"

    def get_video_type(self) -> str:
        return "ShortVideo"

    def calculate_monetization_potential(self) -> float:
        base_score = 0.8
        if self.music_track_id:
            # Popüler müzik 
            base_score += 0.1
        if self.duration_seconds < 15:
            # Çok kısa ise döngüye girer
            base_score += 0.1
        return base_score

    def validate_content_policy(self) -> bool:
        # 60 saniyeden uzun olamaz
        if self.duration_seconds > 60:
            return False
        return True

# Video Service 

class VideoService:
    """
    Video servis sınıfı. 
    İş mantığını (business logic) yönetir. 
    Depo (repository) ile iletişim kurarak veri işlemlerini yapar.
    """
    
    def __init__(self, repository: VideoRepository):
        self.repository = repository

    def create_standard_video(
        self,
        channel_id: str,
        title: str,
        description: str,
        duration_seconds: int,
        visibility: VideoVisibility = VideoVisibility.PRIVATE,
        resolution: str = "1080p"
    ) -> StandardVideo:
        """Standart video oluşturma işlemi."""
        video = StandardVideo(
            channel_id=channel_id,
            title=title,
            description=description,
            duration_seconds=duration_seconds,
            visibility=visibility,
            resolution=resolution
        )
        
        # Politikaları kontrol eder
        if not video.validate_content_policy():
            logger.warning(f"Video ({video.video_id}) kurallara tam uymuyor.")
        
        self.repository.save(video)
        logger.info(f"Standart Video oluşturuldu: {title}")
        return video

    def create_short_video(
        self,
        channel_id: str,
        title: str,
        duration_seconds: int,
        visibility: VideoVisibility = VideoVisibility.PUBLIC,
        music_track_id: Optional[str] = None
    ) -> ShortVideo:
        """Shorts oluşturma."""
        video = ShortVideo(
            channel_id=channel_id,
            title=title,
            description="Short video",
            duration_seconds=duration_seconds,
            visibility=visibility,
            music_track_id=music_track_id
        )
        
        # Shorts kuralları katıdır, hata fırlatabiliriz
        if not video.validate_content_policy():
             raise VideoUploadError("Shorts süresi 60 saniyeyi geçemez.")

        self.repository.save(video)
        logger.info(f"Short Video oluşturuldu: {video.video_id}")
        return video

    def create_live_stream(
        self,
        channel_id: str,
        title: str,
        scheduled_time: Optional[datetime] = None
    ) -> LiveStreamVideo:
        """Canlı yayın oluşturma."""
        video = LiveStreamVideo(
            channel_id=channel_id,
            title=title,
            description="Canlı Yayın",
            scheduled_start_time=scheduled_time,
            visibility=VideoVisibility.PUBLIC
        )
        self.repository.save(video)
        logger.info(f"Canlı Yayın planlandı: {title}")
        return video

    def upload_video(self, video_id: str, file_content: bytes) -> bool:
        """
        Dosya yükleme
        
        Args:
            video_id (str): Video ID
            file_content (bytes): Dosya içeriği (binary)
        
        Returns:
            bool: Başarılı ise True
        """
        video = self.repository.get_by_id(video_id)
        
        logger.info(f"Yükleme başladı: {video.title} (Boyut: {len(file_content)} bytes)...")
        # Simülasyon: Dosya boyutu büyükse biraz bekleyelim
        delay = min(0.5, len(file_content) / 1000000) 
        time.sleep(delay) 
        
        if not file_content:
            raise VideoUploadError("Dosya boş yükleme iptal edildi.")
            
        logger.info("Yükleme tamamlandı.")
        return True

    def process_video(self, video_id: str, channel_obj=None):
        """
        Video işleme ve Modüller Arası Denetim (Entegrasyon)
        """
        # Circular Import'u önlemek için metod içinde import yapıyoruz
        from app.modules.module_1.implementations import KidsChannel

        video = self.repository.get_by_id(video_id)

        try:
            video.transition_status(VideoStatus.PROCESSING)
            logger.info(f"İşleniyor: {video.title}...")

            # --- MODÜLLER ARASI İLETİŞİM (DENETİM) ---
            # Eğer kanal bir Çocuk Kanalı ise ve video 10 dk'dan uzunsa ENGELLE
            if isinstance(channel_obj, KidsChannel) and video.duration_seconds > 600:
                video.transition_status(VideoStatus.BLOCKED)
                logger.warning(f"!!! ENTEGRASYON UYARISI !!!")
                logger.warning(f"Kanal Tipi: {type(channel_obj).__name__} | Kanal Adı: {channel_obj.name}")
                logger.warning(f"Hata: Çocuk kanalına {video.duration_seconds} saniyelik uzun video yüklenemez!")
                self.repository.save(video)
                return  # İşlemi burada kes ve yayınlama
            # ------------------------------------------

            # Normal İçerik Politikası Kontrolü
            if not video.validate_content_policy():
                video.transition_status(VideoStatus.BLOCKED)
                logger.warning(f"İşleme sırasında uygunsuz içerik: {video.video_id}")
            else:
                video.transition_status(VideoStatus.PUBLISHED)
                logger.info(f"Yayınlandı: {video.title}")

            self.repository.save(video)

        except Exception as e:
            logger.error(f"İşlem hatası: {e}")
            raise

    def _simulate_transcoding(self, video: VideoBase):
        """Dahili metot: Transcoding adımlarını simüle eder."""
        steps = ["Demuxing", "Decoding", "Encoding 1080p", "Encoding 720p", "Muxing"]
        pass

    def block_video(self, video_id: str, reason: str):
        """Admin tarafından engelleme."""
        video = self.repository.get_by_id(video_id)
        video.transition_status(VideoStatus.BLOCKED)
        self.repository.save(video)
        logger.warning(f"Video engellendi ({video.title}). Sebep: {reason}")

    def list_videos_by_channel(self, channel_id: str) -> List[VideoBase]:
        return self.repository.find_by_channel(channel_id)

    def search_videos(
        self,
        query: Optional[str] = None,
        visibility: Optional[VideoVisibility] = None,
        min_duration: Optional[int] = None
    ) -> List[VideoBase]:
        """Arama ve filtreleme fonksiyonu."""
        all_videos = self.repository.find_all()
        results = []
        
        for video in all_videos:
            match = True
            if visibility and video.visibility != visibility:
                match = False
            if min_duration and video.duration_seconds < min_duration:
                match = False
            if query and query.lower() not in video.title.lower():
                match = False
            
            if match:
                results.append(video)
                
        return results

    def get_video_statistics(self, video_id: str) -> Dict[str, Any]:
        """Video detayları ve istatistikleri."""
        video = self.repository.get_by_id(video_id)
        return {
            "video_id": video.video_id,
            "views": getattr(video, '_view_count', 0),
            "likes": getattr(video, '_likes', 0),
            "monetization_score": video.calculate_monetization_potential(),
            "type": video.get_video_type()
        }


    def bulk_upload_simulation(self, uploads: List[Dict[str, Any]]):
        """
        Toplu video yükleme
        
        Args:
            uploads: Yüklenecek video bilgilerini içeren sözlük listesi.
        """
        logger.info(f"Toplu yükleme başlatıldı. Toplam: {len(uploads)} video.")
        for item in uploads:
            try:
                self.create_standard_video(
                    channel_id=item['channel_id'],
                    title=item['title'],
                    description=item.get('description', ''),
                    duration_seconds=item['duration'],
                    visibility=item.get('visibility', VideoVisibility.PRIVATE)
                )
            except Exception as e:
                logger.error(f"Toplu yükleme hatası ({item.get('title')}): {e}")
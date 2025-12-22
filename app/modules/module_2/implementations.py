"""
Video Uygulamaları ve Servisleri (Implementations)
==================================================

Bu modül, `VideoBase` soyut sınıfının somut uygulamalarını ve video iş mantığını yöneten servis sınıfını içerir.

Bu dosya şunları içerir:
1. Video Entities: StandardVideo, LiveStreamVideo, ShortVideo
2. Video Service: VideoService
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
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("VideoModule")

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
        
        # Metadata nesnesini de başlatma aşaması 
        self.metadata = VideoMetadata(resolution=resolution)

    def get_video_type(self) -> str:
        return "StandardVideo"

    def calculate_monetization_potential(self) -> float:
        """
        Gelir potansiyeli hesaplama.
        10 dakikadan uzunsa daha çok reklam koyar.
        """
        base_score = 1.0
        
        # 10 dakika kontrolü
        if self.duration_seconds > 600:
            base_score += 0.5
        elif self.duration_seconds < 60:
            base_score -= 0.2 # Çok kısaysa daha az gelir elde edilir
            
        # Çözünürlük kontrolü
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
            return False 
        if self.duration_seconds < 5:
            return False
        return True
    # Açıklamasız video olmaz
        
    def set_resolution(self, resolution: str):
        self.resolution = resolution
        self.metadata.update_resolution(resolution)

    def toggle_comments(self):
        """Yorumları açıp/kapat yapmak için."""
        self.allow_comments = not self.allow_comments


class LiveStreamVideo(VideoBase):
    """
    Canlı yayın nesnesi.
    Normal videodan farkı, başta süresinin belli olmaması ve planlama yapılabilmesi.
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
        super().__init__(channel_id, title, description, 0, visibility, tags)
        self.scheduled_start_time = scheduled_start_time
        self.is_live = False
        self.chat_enabled = chat_enabled
        self.max_concurrent_viewers = 0

    def get_video_type(self) -> str:
        return "LiveStreamVideo"

    def calculate_monetization_potential(self) -> float:
        base_score = 1.5 
        if self.chat_enabled:
            base_score += 0.5
        if self.scheduled_start_time:
            base_score += 0.2 
        return base_score

    def validate_content_policy(self) -> bool:
        if not self.title:
            return False
        return True

    def transition_status(self, new_status: VideoStatus):
        """
        Override: Canlı yayınlar direkt 'Yayında' (PUBLISHED) durumuna geçebilir.
        Processing aşamasını atlayabilirler.
        """
        # Uploaded -> Published geçişine izin ver.
        if self._status == VideoStatus.UPLOADED and new_status == VideoStatus.PUBLISHED:
            self._status = new_status
            if self._published_at is None:
                self._published_at = datetime.now()
            return

        # Diğer durumlar için normal akış devam eder.
        super().transition_status(new_status)

    def start_stream(self):
        """Yayını başlatır."""
        self.is_live = True
        self.transition_status(VideoStatus.PUBLISHED)
    
    def end_stream(self, duration_seconds: int):
        """Yayını bitirir ve toplam süreyi kaydeder."""
        self.is_live = False
        self._duration_seconds = duration_seconds
        # TODO: Burada tekrar izleme kaydı oluşturulabilir.


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
        self.aspect_ratio = "9:16"
        # En boy oranı sabit 9:16 olarak ayarlansın.

    def get_video_type(self) -> str:
        return "ShortVideo"

    def calculate_monetization_potential(self) -> float:
        base_score = 0.8
        if self.music_track_id:
            base_score += 0.1
        if self.duration_seconds < 15:
            base_score += 0.1
        return base_score
    # Video çok kısa ise döngüye girer

    def validate_content_policy(self) -> bool:
        if self.duration_seconds > 60:
            return False
        return True
    # 60 saniyeden uzun olamaz
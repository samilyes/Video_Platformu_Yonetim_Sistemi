"""
Video Modülü - Service Katmanı
=============================

Bu dosya, video iş mantığını içeren servis sınıflarını barındırır.
Video oluşturma, yükleme, işleme ve yönetim iş akışlarını kapsar.
"""

from __future__ import annotations

import time
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from .base import (
    VideoBase,
    VideoVisibility,
    VideoStatus,
    VideoUploadError,
)
from .repository import VideoRepository

logger = logging.getLogger("VideoModule")


class VideoService:
    """Video iş akışlarını yöneten servis katmanı."""

    def __init__(self, repository: VideoRepository):
        self.repository = repository

    def create_standard_video(
        self,
        channel_id: str,
        title: str,
        description: str,
        duration_seconds: int,
        visibility: VideoVisibility = VideoVisibility.PRIVATE,
        resolution: str = "1080p",
    ):
        """Standart video oluşturur ve depoya kaydeder."""
        # Lazy import: Döngüsel import riskini azaltmak için entity'ler burada içe aktarılır.
        from .implementations import StandardVideo

        video = StandardVideo(
            channel_id=channel_id,
            title=title,
            description=description,
            duration_seconds=duration_seconds,
            visibility=visibility,
            resolution=resolution,
        )

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
        music_track_id: Optional[str] = None,
    ):
        """Shorts oluşturur ve depoya kaydeder."""
        from .implementations import ShortVideo

        video = ShortVideo(
            channel_id=channel_id,
            title=title,
            description="Short video",
            duration_seconds=duration_seconds,
            visibility=visibility,
            music_track_id=music_track_id,
        )

        # ShortVideo kuralı: süre 60 saniyeyi aşamaz.
        # Kullanıcı bazen duration'ı dışarıdan değiştirirse (veya validate bozulursa) burada kesin kontrol yapılır.
        if duration_seconds > 60:
            raise VideoUploadError("Shorts süresi 60 saniyeyi geçemez.")

        if not video.validate_content_policy():
            raise VideoUploadError("Shorts içerik politikası doğrulamasından geçemedi.")

        self.repository.save(video)
        logger.info(f"Short Video oluşturuldu: {video.video_id}")
        return video

    def create_live_stream(
        self,
        channel_id: str,
        title: str,
        scheduled_time: Optional[datetime] = None,
    ):
        """Canlı yayın oluşturur ve depoya kaydeder."""
        from .implementations import LiveStreamVideo

        video = LiveStreamVideo(
            channel_id=channel_id,
            title=title,
            description="Canlı Yayın",
            scheduled_start_time=scheduled_time,
            visibility=VideoVisibility.PUBLIC,
        )
        self.repository.save(video)
        logger.info(f"Canlı Yayın planlandı: {title}")
        return video

    def upload_video(self, video_id: str, file_content: bytes) -> bool:
        """Dosya yüklemeyi simüle eder."""
        video = self.repository.get_by_id(video_id)

        logger.info(
            f"Yükleme başladı: {video.title} (Boyut: {len(file_content)} bytes)..."
        )
        delay = min(0.5, len(file_content) / 1_000_000)
        time.sleep(delay)

        if not file_content:
            raise VideoUploadError("Dosya boş yükleme iptal edildi.")

        logger.info("Yükleme tamamlandı.")
        return True

    def process_video(self, video_id: str, channel_obj=None):
        """Video işleme akışını yürütür ve durum geçişlerini uygular."""
        video = self.repository.get_by_id(video_id)

        try:
            video.transition_status(VideoStatus.PROCESSING)
            logger.info(f"İşleniyor: {video.title}...")

            # MODÜLLER ARASI DENETİM
            # Kanal bir KidsChannel ise ve video 10 dk'dan uzunsa ENGELLE.
            if channel_obj is not None:
                try:
                    from app.modules.module_1.implementations import KidsChannel

                    if isinstance(channel_obj, KidsChannel) and video.duration_seconds > 600:
                        video.transition_status(VideoStatus.BLOCKED)
                        logger.warning("ENTEGRASYON UYARISI")
                        logger.warning(
                            f"Kanal Tipi: {type(channel_obj).__name__} | Kanal Adı: {getattr(channel_obj, 'name', '-') }"
                        )
                        logger.warning(
                            f"Hata: Çocuk kanalına {video.duration_seconds} saniyelik uzun video yüklenemez!"
                        )
                        self.repository.save(video)
                        return
                except Exception:
                    # module_1 mevcut değilse veya import başarısızsa entegrasyon kontrolünü es geç.
                    pass

            # Normal içerik kural kontrolleri
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

    def block_video(self, video_id: str, reason: str):
        """Admin tarafından video engeller."""
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
        min_duration: Optional[int] = None,
    ) -> List[VideoBase]:
        """Arama ve filtreleme."""
        all_videos = self.repository.find_all()
        results: List[VideoBase] = []

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
            "views": getattr(video, "_view_count", 0),
            "likes": getattr(video, "_likes", 0),
            "monetization_score": video.calculate_monetization_potential(),
            "type": video.get_video_type(),
        }

    def bulk_upload_simulation(self, uploads: List[Dict[str, Any]]):
        """Toplu video oluşturmayı simüle eder."""
        logger.info(f"Toplu yükleme başlatıldı. Toplam: {len(uploads)} video.")
        for item in uploads:
            try:
                self.create_standard_video(
                    channel_id=item["channel_id"],
                    title=item["title"],
                    description=item.get("description", ""),
                    duration_seconds=item["duration"],
                    visibility=item.get("visibility", VideoVisibility.PRIVATE),
                )
            except Exception as e:
                logger.error(f"Toplu yükleme hatası ({item.get('title')}): {e}")
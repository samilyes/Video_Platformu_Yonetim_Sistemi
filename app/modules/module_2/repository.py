"""
Video Repository (Veri Erişimi)

Veritabanı işlemlerini simüle eden katman.
Bu katman, verilerin (Video nesneleri) kalıcı olarak saklanması, sorgulanması ve yönetilmesinden sorumludur.
"""

from typing import List, Optional, Dict, Union
from datetime import datetime
from .base import VideoBase, VideoStatus, VideoVisibility, VideoNotFoundError

class VideoRepository:
    """
    Video nesnelerini yöneten depo sınıfıdır.
    CRUD (Create, Read, Update, Delete) işlemleri burada yapılır.
    Repository Pattern kullanılarak veri erişimi soyutlanmış olur.
    """

    def __init__(self):
        # Veritabanı tablosunu simüle eder.
        self._videos: Dict[str, VideoBase] = {}
        self._channel_index: Dict[str, List[str]] = {} 

    def save(self, video: VideoBase) -> VideoBase:
        """
        Bir videoyu depoya kaydeder.
        Eğer video zaten varsa günceller, yoksa yeni ekler.
        Ayrıca indeksleri günceller.
        """
        # Veriyi kaydeder
        self._videos[video.video_id] = video
        
        # Kanal indeksini günceller
        if video.channel_id not in self._channel_index:
            self._channel_index[video.channel_id] = []
        if video.video_id not in self._channel_index[video.channel_id]:
            self._channel_index[video.channel_id].append(video.video_id)
            
        return video

    def find_by_id(self, video_id: str) -> Optional[VideoBase]:
        """
        ID ile video bulur.
        """
        return self._videos.get(video_id)

    def get_by_id(self, video_id: str) -> VideoBase:
        video = self.find_by_id(video_id)
        if not video:
            raise VideoNotFoundError(video_id)
        return video

    def delete(self, video_id: str) -> bool:
        """
        Videoyu siler.
        """
        if video_id in self._videos:
            video = self._videos[video_id]
            
            # İndeksten sil
            if video.channel_id in self._channel_index:
                if video_id in self._channel_index[video.channel_id]:
                    self._channel_index[video.channel_id].remove(video_id)
            
            del self._videos[video_id]
            return True
        return False

    def find_all(self) -> List[VideoBase]:
        """
        Tüm videoları listeler.
        """
        return list(self._videos.values())

    def find_by_channel(self, channel_id: str) -> List[VideoBase]:
        """
        Belirli bir kanala ait videoları filtreler.
        İndeks kullanarak daha hızlı erişim sağlar.
        """
        # İndeksten ID'leri al
        video_ids = self._channel_index.get(channel_id, [])
        
        # Nesneleri getir
        return [self._videos[vid] for vid in video_ids if vid in self._videos]

    def filter_videos(
        self,
        status: Optional[VideoStatus] = None,
        visibility: Optional[VideoVisibility] = None,
        channel_id: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[VideoBase]:
        """
Videoları verilen kriterlere göre süzer.

Bu metot, farklı filtreleme senaryolarını desteklemek için tasarlanmıştır.
Parametrelerin tamamı isteğe bağlıdır; yalnızca belirtilenler dikkate alınır.

Parametreler:
    status (Optional[VideoStatus]):
        Videonun durumuna göre filtreleme yapar
        (ör. yalnızca yayında olan videolar).

    visibility (Optional[VideoVisibility]):
        Videonun görünürlük ayarına göre filtreler
        (ör. yalnızca herkese açık videolar).

    channel_id (Optional[str]):
        Belirli bir kanala ait videoları getirir.

    date_from (Optional[datetime]):
        Bu tarihten sonra oluşturulan videoları getirir.

    date_to (Optional[datetime]):
        Bu tarihten önce oluşturulan videoları getirir.

Dönüş değeri:
    List[VideoBase]:
        Filtrelere uyan videoların listesi.
        Hiçbir filtre belirtilmezse tüm videolar döndürülür.
"""

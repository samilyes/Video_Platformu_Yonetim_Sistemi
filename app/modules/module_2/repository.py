"""
Video Repository (Veri Erişimi)
===============================

Veritabanı işlemlerini simüle eden katmandır.
Bu katman, verilerin kalıcı olarak saklanması, sorgulanması ve yönetilmesinden sorumludur.
"""

from typing import List, Optional, Dict, Union
from datetime import datetime
from .base import VideoBase, VideoStatus, VideoVisibility, VideoNotFoundError

class VideoRepository:
    """
    Video nesnelerini yöneten depo sınıfıdır.
    Create, read, update, delete işlemleri burada yapılır.
    Repository kullanılarak veri erişimi soyutlanır.
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
        
        Argümanlar:
            video (VideoBase): Kaydedilecek video nesnesi.
            
        Döndürür:
            VideoBase: Kaydedilen video nesnesi.
        """
        # Veriyi kaydet
        self._videos[video.video_id] = video
        
        # Kanal indeksini güncelle
        if video.channel_id not in self._channel_index:
            self._channel_index[video.channel_id] = []
        if video.video_id not in self._channel_index[video.channel_id]:
            self._channel_index[video.channel_id].append(video.video_id)
            
        return video

    def find_by_id(self, video_id: str) -> Optional[VideoBase]:
        """
        ID ile video bulur.
        
        Argümanlar:
            video_id: Video ID'si.
            
        Döndürür:
            Optional[VideoBase]: Bulunursa nesne, bulunamazsa None döner.
        """
        return self._videos.get(video_id)

    def get_by_id(self, video_id: str) -> VideoBase:
        """
        ID ile video bulur, yoksa hata verir.
        
        Argümanlar:
            video_id : Video ID'si.
            
        Döndürür:
            VideoBase: Bulunan video nesnesi.
            
        Raise eder:
            VideoNotFoundError: Video bulunamazsa hata verir.
        """
        video = self.find_by_id(video_id)
        if not video:
            raise VideoNotFoundError(video_id)
        return video

    def delete(self, video_id: str) -> bool:
        """
        Videoyu siler.
        
        Argümanlar:
            video_id (str): Silinecek video ID'si.
            
        Döndürür:
            bool: Silme başarılıysa True, aksi halde False dödürür.
        """
        if video_id in self._videos:
            video = self._videos[video_id]
            if video.channel_id in self._channel_index:
                if video_id in self._channel_index[video.channel_id]:
                    self._channel_index[video.channel_id].remove(video_id) 
            del self._videos[video_id]
            return True
        return False
    # İndeksten siler.

    def find_all(self) -> List[VideoBase]:
        """
        Tüm videoları listeler.
        
        Returns:
            List[VideoBase]: Video listesi.
        """
        return list(self._videos.values())

    def find_by_channel(self, channel_id: str) -> List[VideoBase]:
        """
        Belirli bir kanala ait videoları filtreler.
        İndeks kullanarak daha hızlı erişim sağlar.
        
        Args:
            channel_id: Kanal ID'si.
            
        Returns:
            List[VideoBase]: O kanala ait videolar.
        """
        # İndeksten ID'leri alır.
        video_ids = self._channel_index.get(channel_id, [])
        # Nesneleri getirir.
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
        Videoları belirli kriterlere göre filtreler.
        Bu metot, karmaşık sorguları simüle etmek için kullanılır.
        Her parametre opsiyoneldir; sadece verilen parametreler filtrelemeye dahil edilir.

        Argümanlar:
            status: Videonun durumuna göre filtreleme yapar.
                (Örn: Sadece YAYINDA olanları getirir.).
           
            visibility: Görünürlük ayarına göre filtreler.
                (Örn: Sadece PUBLIC olan videolardır.).
            
            channel_id: Belirli bir kanalın videolarını getirir.
            date_from: Oluşturulma tarihi bu tarihten sonra olanlar.
            date_to: Oluşturulma tarihi bu tarihten önce olanlar.

        Döndürür:
            List[VideoBase]: Kriterlere uyan Video nesnelerinin listesi.
            Eğer hiçbir kriter verilmezse tüm videoları döndürür.
        """
        # Başlangıç kümesi: Kanal ID varsa indeksten, yoksa hepsinden alır.
        if channel_id:
            start_list = self.find_by_channel(channel_id)
        else:
            start_list = list(self._videos.values())

        results = []
        for v in start_list:
            # Durum kontrolü
            if status and v.status != status:
                continue
            
            # Görünürlük kontrolü
            if visibility and v.visibility != visibility:
                continue
                
            # Tarih aralığı kontrolü (Başlangıç)
            if date_from and v.created_at < date_from:
                continue
                
            # Tarih aralığı kontrolü (Bitiş)
            if date_to and v.created_at > date_to:
                continue
                
            results.append(v)

        return results

    def count(self) -> int:
        """
        Depodaki toplam video sayısını döndürür.
        """
        return len(self._videos)

    def clear(self):
        """
        Depoyu tamamen temizler.
        Bu işlem geri alınamaz.
        """
        self._videos.clear()
        self._channel_index.clear()
    
    def exists(self, video_id: str) -> bool:
        """Video var mı kontrol eder."""
        return video_id in self._videos
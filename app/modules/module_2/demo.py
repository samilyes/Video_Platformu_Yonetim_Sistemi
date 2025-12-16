"""
Demo Scripti
===========
Bu script modülün nasıl çalıştığını test etmek ve göstermek için yazılır.
Senaryo oldukça kapsamlıdır ve modülün tüm özelliklerini simüle eder.
"""

import time
import sys
from datetime import datetime, timedelta
from .base import VideoVisibility, VideoStatus, VideoError
from .repository import VideoRepository
from .implementations import VideoService

def print_header(title: str):
    """Konsola şık bir başlık koyar."""
    print("\n" + "="*60)
    print(f"   {title.upper()}")
    print("="*60)
    time.sleep(0.5)

def print_step(step_num: int, description: str):
    """Adım bilgisini gösterir."""
    print(f"\n>>> ADIM {step_num}: {description}")
    print("-" * 40)
    time.sleep(0.3)

def run_demo():
    print_header("SMART VIDEO PLATFORM - KAPSAMLI DEMO SENARYOSU")

    # ADIM 1: Başlatma

    print_step(1, "Sistem Başlatılıyor.")
    repo = VideoRepository()
    service = VideoService(repo)
    print(f"[SİSTEM] Repository oluşturuldu: {repo}")
    print(f"[SİSTEM] Service katmanı aktif: {service}")
    print("[SİSTEM] Veritabanı hazır.")
    
    # ADIM 2: Video Oluşturma
    
    print_step(2, "İçerik Üreticileri Video Oluşturuyor.")
    
    # Eğitim Kanalı
    channel_edu = "channel_tech_edu_001"
    
    print(f"[USER] '{channel_edu}' kanalı yeni bir standart video oluşturuyor.")
    v1 = service.create_standard_video(
        channel_id=channel_edu,
        title="Python ile OOP Dersleri #1",
        description="Nesne Yönelimli Programlamaya kapsamlı bir giriş dersi.",
        duration_seconds=900, # 15 dakika
        visibility=VideoVisibility.PUBLIC,
        resolution="1080p"
    )
    print(f"Oluşturuldu: {v1.title} (ID: {v1.video_id})")
    print(f"Durum: {v1.status.value}, Tür: {v1.get_video_type()}")

    # Short videosu
    print(f"\n[USER] '{channel_edu}' kanalı bir Short video oluşturuyor.")
    v2 = service.create_short_video(
        channel_id=channel_edu,
        title="Python İpucu: List Comprehension Nedir?",
        duration_seconds=45,
        visibility=VideoVisibility.PUBLIC
    )
    print(f" -> Oluşturuldu: {v2.title}")
    print(f"    Süre: {v2.duration_seconds}s (Shorts limiti < 60s)")

    # Oyun Kanalı
    channel_gamer = "channel_gamer_zone_99"
    print(f"\n[USER] '{channel_gamer}' kanalı bir Canlı Yayın planlıyor.")
    v3 = service.create_live_stream(
        channel_id=channel_gamer,
        title="Büyük Turnuva Finali - CANLI",
        scheduled_time=datetime.now() + timedelta(minutes=30)
    )
    print(f" -> Planlandı: {v3.title}")
    print(f"    Planlanan Saat: {v3.scheduled_start_time}")

    # ADIM 3: Yükleme ve İşleme

    print_step(3, "Video Yükleme ve İşleme Süreci.")

    try:
        print(f"[UPLOAD] '{v1.title}' yükleniyor.")
        service.upload_video(v1.video_id, b"dosya_binary_data_mp4")
        
        print(f"[PROCESS] '{v1.title}' işleniyor")
        service.process_video(v1.video_id)
        
        # Son durumu kontrol eder
        updated_v1 = repo.get_by_id(v1.video_id)
        print(f" -> SONUÇ: '{updated_v1.title}' şu an {updated_v1.status.value.upper()} durumunda.")
        
    except VideoError as e:
        print(f"İşlem başarısız: {e}")

    try:
        print(f"\n[UPLOAD] '{v2.title}' yükleniyor.")
        service.upload_video(v2.video_id, b"dosya_binary_data_mov")
        
        print(f"[PROCESS] '{v2.title}' işleniyor.")
        service.process_video(v2.video_id)
        print(f" -> SONUÇ: '{v2.title}' YAYINDA.")
    except Exception as e:
        print(f"[HATA] {e}")

    # ADIM 4: Canlı Yayın Senaryosu
    print_step(4, "Canlı Yayın Başlıyor")
    
    # Yayıncı yayını başlatıyor
    print(f"[STREAM] '{v3.title}' için yayın sinyali gönderiliyor")
    v3.start_stream()
    # Repo'yu güncel tutmak için save tutar
    repo.save(v3)
    
    if v3.is_live:
        print(" -> YAYIN AKTİF (Status: PUBLISHED)")
        print(" -> İzleyici sohbete katılıyor...")
        v3.max_concurrent_viewers = 15000
    
    time.sleep(0.5)
    print("\n[STREAM] Yayın sona eriyor...")
    v3.end_stream(duration_seconds=3600)
    print(f" -> Yayın bitti. Toplam Süre: {v3.duration_seconds} saniye.")
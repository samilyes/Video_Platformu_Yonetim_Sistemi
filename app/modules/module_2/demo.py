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
    
    print(f"'{channel_edu}' kanalı yeni bir standart video oluşturuyor.")
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
    print(f"\n'{channel_edu}' kanalı bir Short video oluşturuyor.")
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
    print(f"\n'{channel_gamer}' kanalı bir Canlı Yayın planlıyor.")
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
        print(f"'{v1.title}' yükleniyor.")
        service.upload_video(v1.video_id, b"dosya_binary_data_mp4")
        
        print(f"'{v1.title}' işleniyor")
        service.process_video(v1.video_id)
        
        # Son durumu kontrol eder
        updated_v1 = repo.get_by_id(v1.video_id)
        print(f" -> SONUÇ: '{updated_v1.title}' şu an {updated_v1.status.value.upper()} durumunda.")
        
    except VideoError as e:
        print(f"İşlem başarısız: {e}")

    try:
        print(f"\n'{v2.title}' yükleniyor.")
        service.upload_video(v2.video_id, b"dosya_binary_data_mov")
        
        print(f"'{v2.title}' işleniyor.")
        service.process_video(v2.video_id)
        print(f" -> SONUÇ: '{v2.title}' YAYINDA.")
    except Exception as e:
        print(f"[HATA] {e}")

    # ADIM 4: Canlı Yayın Senaryosu
    print_step(4, "Canlı Yayın Başlıyor")
    
    # Yayıncı yayını başlatıyor
    print(f"'{v3.title}' için yayın sinyali gönderiliyor")
    v3.start_stream()
    # Repo'yu güncel tutmak için save tutar
    repo.save(v3)
    
    if v3.is_live:
        print(" -> YAYIN AKTİF (Status: PUBLISHED)")
        print(" -> İzleyici sohbete katılıyor...")
        v3.max_concurrent_viewers = 15000
    
    time.sleep(0.5)
    print("\nYayın sona eriyor...")
    v3.end_stream(duration_seconds=3600)
    print(f" -> Yayın bitti. Toplam Süre: {v3.duration_seconds} saniye.")

    # ADIM 5: Analitik ve Raporlama

    print_step(5, "Gelir ve İstatistik Analizi")
    print("Her video türü kendi metodunu kullanır.\n")

    all_videos = repo.find_all()
    total_potential = 0.0

    print(f"{'BAŞLIK':<40} | {'TÜR':<15} | {'PUAN':<5}")
    print("-" * 70)

    for vid in all_videos:
        score = vid.calculate_monetization_potential()
        total_potential += score
        print(f"{vid.title[:38]:<40} | {vid.get_video_type():<15} | {score:.1f}")

    print("-" * 70)
    print(f"Ortalama Platform Puanı: {total_potential / len(all_videos):.2f}")

    # ADIM 6: Filtreleme

    print_step(6, "Gelişmiş Arama ve Filtreleme")
    print("Kanal: 'channel_tech_edu_001' olan videolar aranıyor.")
    edu_videos = service.list_videos_by_channel(channel_edu)
    for v in edu_videos:
        print(f" * {v.title}")

    print("\nSüresi 10 dakikadan uzun videolar.")
    long_videos = service.search_videos(min_duration=600)
    for v in long_videos:
        print(f" * {v.title} ({v.duration_seconds}s)")

    # ADIM 7: Hata Senaryosu ve Admin Engellemesi

    print_step(7, "Yönetici İşlemleri ve Hata Yönetimi")

    # Yeni bir 'sakıncalı' video oluşturma
    v_bad = service.create_short_video(
        channel_id="user_spammer",
        title="Yasaklı İçerik",
        duration_seconds=10,
        visibility=VideoVisibility.PUBLIC
    )
    # Yasaklı videoyu process etme
    service.process_video(v_bad.video_id)
    print(f"Oluşturuldu: {v_bad.title} (Status: {v_bad.status.value})")

    print("\nBu içerik platform kurallarına aykırı bulundu. Engelleniyor.")
    service.block_video(v_bad.video_id, reason="Topluluk Kuralları İhlali")
    
    # Durumu kontrol et
    blocked_v = repo.get_by_id(v_bad.video_id)
    print(f" -> Son Durum: {blocked_v.status.value.upper()}")
    
    # Geçersiz durum testi
    print("\nEngelli videoyu geçersiz duruma almaya çalışma testi.")
    try:
        # BLOCKED -> UPLOADED geçişi mantıken imkansızdır
        blocked_v.transition_status(VideoStatus.UPLOADED)
        print("Mantık hatası var.")
    except Exception as e:
        print(f"Beklenen Hata Yakalandı: {e}")
    print_header("DEMO BAŞARIYLA TAMAMLANDI")
    print(f"Toplam Video Sayısı: {repo.count()}")
    print("Program sonlanıyor.")

if __name__ == "__main__":
    run_demo()
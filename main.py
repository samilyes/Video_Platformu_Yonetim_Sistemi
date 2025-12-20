import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app.modules.module_1.implementations import (
    PersonalChannel, KidsChannel, BrandChannel)

from app.modules.module_2.implementations import (
    ShortVideo, StandardVideo, LiveStreamVideo)


def run_demo():
    print("\n" + "=" * 45)
    print("      YOUTUBE YÖNETİM SİSTEMİ (ENTEGRE MODÜLLER)")
    print("=" * 45 + "\n")

    # servis-repository kuulumu
    from app.modules.module_2.repository import VideoRepository
    from app.modules.module_2.implementations import VideoService
    from app.modules.module_2.base import VideoStatus

    video_repo = VideoRepository()
    video_service = VideoService(video_repo)

    # kanallarin tanitimi
    base_1 = [
        PersonalChannel("CH_01", "Gamer Pro", "Oyun kanalı", "user_1"),
        KidsChannel("CH_02", "Çocuk Dünyası", "Eğitici içerik", "user_2"),
        BrandChannel("CH_03", "Teknoloji A.Ş.", "Resmi marka", "user_3"),
    ]

    # videolarin olusturulup islenmesi
    print("--- ADIM 2: Video Yaşam Döngüsü ve Denetim ---")

    # Test etmeke
    v1 = video_service.create_standard_video("CH_01", "Python Dersi", "OOP Temelleri", 600)
    v2 = video_service.create_standard_video("CH_02", "Uzun Çizgi Film", "Kural İhlali Testi",
                                             1200)  # Kids + 1200sn = BLOCKED
    v3 = video_service.create_short_video("CH_01", "Python İpucu", 30)

    base_2 = [v1, v2, v3]

    for vid in base_2:
        print(f"\n[İŞLEM] Video: {vid.title}")
        associated_channel = next((ch for ch in base_1 if ch.channel_id == vid.channel_id), None)

        video_service.upload_video(vid.video_id, b"test_data")
        # Modül 2, Modül 1'deki nesneyi burada denetler:
        video_service.process_video(vid.video_id, channel_obj=associated_channel)

        print(f"  > Tür: {vid.get_video_type()} | Durum: {vid.status.name}")
        print(f"  > Gelir Puanı: {vid.calculate_monetization_potential()}")

    print("\n" + "=" * 45)
    print("   MODÜLLER ARASI CANLI VERİ ANALİZİ")
    print("=" * 45)

    for n in base_1:
        my_videos = video_repo.find_by_channel(n.channel_id)
        published_vids = [v for v in my_videos if v.status == VideoStatus.PUBLISHED]
        total_score = sum([v.calculate_monetization_potential() for v in my_videos])

        print(f"\nKanal: {n.name} [{type(n).__name__}]")
        print(f"  -> Toplam Video Sayısı (Modül 2'den): {len(my_videos)}")
        print(f"  -> Başarıyla Yayınlanan: {len(published_vids)}")
        print(f"  -> Toplam Gelir Potansiyeli: {round(total_score, 2)} Birim")
        print(f"  -> Erişim Seviyesi: {n.get_access_level()}")

    print("\n" + "=" * 45)
    print("      DEMO BAŞARIYLA TAMAMLANDI")
    print("=" * 45)

if __name__ == "__main__":
    run_demo()
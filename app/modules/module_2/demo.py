# Demo Scripti
# ===========
# Bu script modülün nasıl çalıştığını test etmek ve göstermek için yazılır.
# Senaryo oldukça kapsamlıdır ve modülün tüm özelliklerini simüle eder.

import os
import sys
import time
from datetime import datetime

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.modules.module_2.base import VideoError, VideoStatus, VideoVisibility, format_duration, VideoUploadError
from app.modules.module_2.repository import VideoRepository
from app.modules.module_2.services import VideoService
from app.modules.module_2.implementations import (
        StandardVideo,
        LiveStreamVideo,
        ShortVideo,
    )

def _banner(title: str):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

def _step(title: str):
    print("\n" + "-" * 70)
    print(title)
    print("-" * 70)

def _typewriter(text: str, delay: float = 0.008):
    for ch in text:
        print(ch, end="", flush=True)
        time.sleep(delay)
    print()


def _prompt(msg: str, default: str = "") -> str:
    value = input(msg).strip()
    return value if value else default

def _read_int(msg: str, default: int) -> int:
    # Kullanıcının girdiği değeri int'e çevirir.
    # Geçersiz girişte default döner.
    raw = _prompt(msg, str(default))
    try:
        value = int(raw)
        return value
    except ValueError:
        return default
    
def _choose_visibility(default: VideoVisibility = VideoVisibility.PUBLIC) -> VideoVisibility:
    mapping = {
        "1": VideoVisibility.PUBLIC,
        "2": VideoVisibility.PRIVATE,
        "3": VideoVisibility.UNLISTED,
    }

    print("Görünürlük seç:")
    print("  1) PUBLIC   (herkese açıktır.)")
    print("  2) PRIVATE  (Sadece kanal sahibi görebilir.)")
    print("  3) UNLISTED (liste dışıdır, bağlantıya sahip olanlar görebilir.)")

    choice = _prompt(f"Seçim [varsayılan {default.value}]: ", "").lower()
    return mapping.get(choice, default)

def _print_video(video):
    print(
        f"  • id={video.video_id} | {video} | süre={format_duration(video.duration_seconds)} | görünürlük={video.visibility.value}"
    )

def _menu() -> str:
    print("\n" + "-" * 70)
    print("MENU")
    print("  1) Standart video oluştur")
    print("  2) Short video oluştur")
    print("  3) Canlı yayın oluştur")
    print("  4) Video yükle")
    print("  5) Video işle (PROCESS -> PUBLISH/BLOCK)")
    print("  6) Video engelle")
    print("  7) Kanal videolarını listele")
    print("  8) Arama/filtreleme")
    print("  9) Video istatistikleri")
    print("  0) Çıkış")
    return _prompt("Seçim: ")

def run_demo():
    _banner("AKILLI VİDEO PLATFORMU - MODULE 2 DEMO")
    _typewriter("Sistem başlatılıyor...")

    repo = VideoRepository()
    service = VideoService(repo)

    while True:
        choice = _menu()

        if choice == "0":
            _banner("ÇIKIŞ")
            print(f"Toplam video sayısı: {repo.count()}")
            return

        if choice == "1":
            _step("Standart video oluştur")
            channel_id = _prompt("Kanal ID: ", "channel_tech_edu_001")
            title = _prompt("Başlık: ", "Demo Standard")
            description = _prompt("Açıklama: ", "Açıklama")
            duration = _read_int("Süre (sn): ", 120)
            visibility = _choose_visibility(VideoVisibility.PUBLIC)
            resolution = _prompt("Çözünürlük: ", "1080p")

            v = service.create_standard_video(
                channel_id=channel_id,
                title=title,
                description=description,
                duration_seconds=duration,
                visibility=visibility,
                resolution=resolution,
            )
            print("Oluşturuldu")
            _print_video(v)

        elif choice == "2":
            _step("Short video oluştur")
            channel_id = _prompt("Kanal ID: ", "channel_tech_edu_001")
            title = _prompt("Başlık: ", "Demo Short")
            duration = _read_int("Süre (sn): ", 30)

            # Süre kuralı en başta kontrol edilir; hatalıysa görünürlük sormaya gerek yok.
            if duration > 60:
                print("HATA: Shorts süresi 60 saniyeyi geçemez.")
                continue

            visibility = _choose_visibility(VideoVisibility.PUBLIC)

            try:
                v = service.create_short_video(
                    channel_id=channel_id,
                    title=title,
                    duration_seconds=duration,
                    visibility=visibility,
                )
                print("Oluşturuldu")
                _print_video(v)
            except VideoError as e:
                print(f"HATA: {e}")

        elif choice == "3":
            _step("Canlı yayın oluştur")
            channel_id = _prompt("Kanal ID: ", "channel_gamer_zone_99")
            title = _prompt("Başlık: ", "Demo Live")

            v = service.create_live_stream(
                channel_id=channel_id,
                title=title,
                scheduled_time=datetime.now(),
            )
            print("Oluşturuldu")
            _print_video(v)

            # Canlı yayın akışı
            start = _prompt("Yayını şimdi başlatılsın mı? (e/h) [e]: ", "e").lower()
            if start in ("e", "evet", "y"):
                v.start_stream()
                repo.save(v)
                print(f"Yayın başladı | status={v.status.value}")
                end_dur = _read_int("Yayın süresi (sn): ", 120)
                v.end_stream(end_dur)
                repo.save(v)
                print(f"Yayın bitti | süre={format_duration(v.duration_seconds)}")

        elif choice == "4":
            _step("Video yükle")
            video_id = _prompt("Video ID: ")
            size = _read_int("Dosya boyutu (byte): ", 16)
            payload = b"x" * max(0, size)

            try:
                service.upload_video(video_id, payload)
                print("Yükleme başarılı")
            except VideoError as e:
                print(f"HATA: {e}")

        elif choice == "5":
            _step("Video işle")
            video_id = _prompt("Video ID: ")

            try:
                service.process_video(video_id)
                v = repo.get_by_id(video_id)
                print(f"Son durum: {v.status.value.upper()} | published_at={v.published_at}")
            except VideoError as e:
                print(f"HATA: {e}")

        elif choice == "6":
            _step("Video engelle")
            video_id = _prompt("Video ID: ")
            reason = _prompt("Sebep: ", "Kural ihlali")

            try:
                service.block_video(video_id, reason)
                v = repo.get_by_id(video_id)
                print(f"Engellendi: {v.title} | status={v.status.value.upper()}")
            except VideoError as e:
                print(f"HATA: {e}")

        elif choice == "7":
            _step("Kanal videolarını listele")
            channel_id = _prompt("Kanal ID: ")
            videos = service.list_videos_by_channel(channel_id)
            print(f"Bulunan video: {len(videos)}")
            for v in videos:
                _print_video(v)

        elif choice == "8":
            _step("Arama/filtreleme")
            query = _prompt("Başlık içinde ara: ", "")
            min_dur = _read_int("Minimum süre (sn): ", 0)
            visibility = _choose_visibility(VideoVisibility.PUBLIC)

            results = service.search_videos(
                query=query if query else None,
                min_duration=min_dur if min_dur > 0 else None,
                visibility=visibility,
            )

            print(f"Bulunan video: {len(results)}")
            for v in results:
                _print_video(v)

        elif choice == "9":
            _step("Video istatistikleri")
            video_id = _prompt("Video ID: ")

            try:
                stats = service.get_video_statistics(video_id)
                print(f"video_id: {stats['video_id']}")
                print(f"type: {stats['type']}")
                print(f"views: {stats['views']}")
                print(f"likes: {stats['likes']}")
                print(f"monetization_score: {stats['monetization_score']:.2f}")
            except VideoError as e:
                print(f"HATA: {e}")

        else:
            print("Geçersiz seçim")


if __name__ == "__main__":
    run_demo()
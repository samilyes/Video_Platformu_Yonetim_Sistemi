import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

import unittest
from datetime import datetime, timedelta


# İçe aktarma yollarını yönetmek için (Testlerin farklı dizinlerden çalıştırılabilmesi için)
try:
    # Modül içi import (Eğer bir paket parçası olarak çalıştırılırsa)
    from app.modules.module_2.base import (
        VideoBase,
        VideoStatus,
        VideoVisibility,
        VideoError,
        VideoNotFoundError,
        InvalidVideoStatusError,
        validate_video_title,
        format_duration,
    )
    from app.modules.module_2.implementations import (
        StandardVideo,
        LiveStreamVideo,
        ShortVideo,
    )
    from app.modules.module_2.services import VideoService
    from app.modules.module_2.repository import VideoRepository
except ImportError:
    # Kök dizinden veya doğrudan çalıştırılırsa
    try:
        from app.modules.module_2.base import (
            VideoBase,
            VideoStatus,
            VideoVisibility,
            VideoError,
            VideoNotFoundError,
            InvalidVideoStatusError,
            validate_video_title,
            format_duration,
        )
        from app.modules.module_2.implementations import (
            StandardVideo,
            LiveStreamVideo,
            ShortVideo,
        )
        from app.modules.module_2.services import VideoService
        from app.modules.module_2.repository import VideoRepository
    except ImportError:
        # Son çare: sys.path manipülasyonu (Kullanıcının init.py'sine benzer)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)

        from app.modules.module_2.base import (
            VideoBase,
            VideoStatus,
            VideoVisibility,
            VideoError,
            VideoNotFoundError,
            InvalidVideoStatusError,
            validate_video_title,
            format_duration,
        )
        from app.modules.module_2.implementations import (
            StandardVideo,
            LiveStreamVideo,
            ShortVideo,
        )
        from app.modules.module_2.services import VideoService
        from app.modules.module_2.repository import VideoRepository


class TestVideoBaseAndUtils(unittest.TestCase):
    """Base sınıf, yardımcı fonksiyonlar ve exception testleri."""

    def test_utils_validate_title(self):
        """Başlık doğrulama fonksiyonunu test eder."""
        self.assertTrue(validate_video_title("Normal Başlık"))
        self.assertFalse(validate_video_title(""))
        self.assertFalse(validate_video_title("A" * 101))  # Çok uzun
        self.assertFalse(validate_video_title("<script>alert</script>"))  # Yasaklı karakter

    def test_utils_format_duration(self):
        """Süre formatlama fonksiyonunu test eder."""
        self.assertEqual(format_duration(65), "01:05")
        self.assertEqual(format_duration(3665), "01:01:05")
        self.assertEqual(format_duration(0), "00:00")

    def test_video_base_abstract(self):
        """VideoBase'in abstract olduğu için direkt oluşturulamadığını doğrular."""
        with self.assertRaises(TypeError):
            VideoBase("c1", "Title", "Desc", 100)

    def test_preview_object_creation(self):
        """Factory method create_preview_object test eder."""
        preview = StandardVideo.create_preview_object("Preview Test", 60)
        self.assertIsNotNone(preview)
        self.assertEqual(preview.title, "ÖNİZLEME: Preview Test")
        self.assertEqual(preview.channel_id, "PREVIEW_CHANNEL")


class TestVideoImplementations(unittest.TestCase):
    """Alt sınıfların (Subclasses) ve Polymorphism testleri."""

    def test_standard_video(self):
        v = StandardVideo("c1", "Std Video", "Desc", 600, resolution="4K")
        self.assertEqual(v.get_video_type(), "StandardVideo")

        # Monetization: Base(1.0) + Duration(>600 yok, tam 600) + 4K(0.3) = 1.3
        self.assertAlmostEqual(v.calculate_monetization_potential(), 1.3)

        # Policy
        self.assertTrue(v.validate_content_policy())

        # Description boşsa hata
        v.description = ""
        self.assertFalse(v.validate_content_policy())

    def test_short_video(self):
        v = ShortVideo("c1", "Shorty", "Desc", 45)
        self.assertEqual(v.get_video_type(), "ShortVideo")
        self.assertAlmostEqual(v.calculate_monetization_potential(), 0.8)

        # Policy: 60sn üzeri olamaz
        v._duration_seconds = 61
        self.assertFalse(v.validate_content_policy())

    def test_live_stream_video(self):
        v = LiveStreamVideo("c1", "Live Now", "Desc", chat_enabled=True)
        self.assertEqual(v.get_video_type(), "LiveStreamVideo")
        self.assertAlmostEqual(v.calculate_monetization_potential(), 2.0)

        # Durum geçişi (Live özel durumu: Uploaded -> Published direkt olabilir)
        v.start_stream()
        self.assertEqual(v.status, VideoStatus.PUBLISHED)
        self.assertTrue(v.is_live)

        v.end_stream(3600)
        self.assertFalse(v.is_live)
        self.assertEqual(v.duration_seconds, 3600)


class TestVideoRepository(unittest.TestCase):
    """Repository CRUD ve Filtreleme testleri."""

    def setUp(self):
        self.repo = VideoRepository()
        self.v1 = StandardVideo("chan1", "V1", "D1", 100, visibility=VideoVisibility.PUBLIC)
        self.v2 = StandardVideo("chan1", "V2", "D2", 200, visibility=VideoVisibility.PRIVATE)
        self.v3 = ShortVideo("chan2", "V3", "D3", 50, visibility=VideoVisibility.PUBLIC)

    def test_save_and_get(self):
        self.repo.save(self.v1)
        fetched = self.repo.get_by_id(self.v1.video_id)
        self.assertEqual(fetched, self.v1)
        self.assertTrue(self.repo.exists(self.v1.video_id))

    def test_find_not_found(self):
        with self.assertRaises(VideoNotFoundError):
            self.repo.get_by_id("non-existent-id")

    def test_delete(self):
        self.repo.save(self.v1)
        self.assertTrue(self.repo.delete(self.v1.video_id))
        self.assertFalse(self.repo.exists(self.v1.video_id))

    def test_filter_videos(self):
        self.repo.save(self.v1)
        self.repo.save(self.v2)
        self.repo.save(self.v3)

        # Kanal filtresi
        chan1_videos = self.repo.filter_videos(channel_id="chan1")
        self.assertEqual(len(chan1_videos), 2)

        # Görünürlük filtresi
        public_videos = self.repo.filter_videos(visibility=VideoVisibility.PUBLIC)
        self.assertEqual(len(public_videos), 2)  # V1 ve V3

        # Karma filtre (Chan1 ve Private)
        private_chan1 = self.repo.filter_videos(channel_id="chan1", visibility=VideoVisibility.PRIVATE)
        self.assertEqual(len(private_chan1), 1)
        self.assertEqual(private_chan1[0].title, "V2")

    def test_count_and_clear(self):
        self.repo.save(self.v1)
        self.assertEqual(self.repo.count(), 1)
        self.repo.clear()
        self.assertEqual(self.repo.count(), 0)


class TestVideoService(unittest.TestCase):
    """Service katmanı iş mantığı testleri."""

    def setUp(self):
        self.repo = VideoRepository()
        self.service = VideoService(self.repo)

    def test_create_flow(self):
        v = self.service.create_standard_video("c1", "New Video", "Desc", 120)
        self.assertIsNotNone(v.video_id)
        self.assertIn(v.video_id, self.repo._videos)

    def test_upload_process_publish_flow(self):
        v = self.service.create_standard_video("c1", "Flow Test", "Desc", 120)

        # Upload
        self.service.upload_video(v.video_id, b"data")

        # Process (Processing -> Published)
        self.service.process_video(v.video_id)
        self.assertEqual(v.status, VideoStatus.PUBLISHED)

    def test_block_video(self):
        v = self.service.create_standard_video("c1", "Bad Video", "Desc", 120)
        self.service.block_video(v.video_id, "Violation")
        self.assertEqual(v.status, VideoStatus.BLOCKED)

    def test_invalid_transition(self):
        """Geçersiz durum geçişini test eder."""
        v = self.service.create_standard_video("c1", "Test", "Desc", 120)
        with self.assertRaises(InvalidVideoStatusError):
            v.transition_status(VideoStatus.PUBLISHED)

    def test_search_videos(self):
        self.service.create_standard_video("c1", "Python Tutorial", "Desc", 600)
        self.service.create_standard_video("c1", "Java Tutorial", "Desc", 600)

        results = self.service.search_videos(query="Python")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Python Tutorial")

    def test_bulk_upload_simulation(self):
        """Toplu yükleme metodunu test eder."""
        uploads = [
            {"channel_id": "c1", "title": "V1", "duration": 100},
            {"channel_id": "c1", "title": "V2", "duration": 200},
        ]
        self.service.bulk_upload_simulation(uploads)
        self.assertEqual(self.repo.count(), 2)


if __name__ == "__main__":
    unittest.main()

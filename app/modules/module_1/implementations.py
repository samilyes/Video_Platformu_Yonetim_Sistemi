from .base import BaseChannel, ChannelType, UserRole


# Exceptions
class InvalidNameError(Exception): pass


class ChannelLimitReachedError(Exception): pass


class InvalidAgeRangeError(Exception): pass


class ContentNotAllowedError(Exception): pass


class BrandVerificationError(Exception): pass


class SubscriptionRequiredError(Exception): pass

class PersonalChannel(BaseChannel):

    def __init__(self, channel_id, name, description, owner_id):
        if len(name) < 5:
            raise InvalidNameError(f"Channel name '{name}' is too short")
        super().__init__(channel_id, name, description, owner_id, ChannelType.PERSONAL)
        self._max_videos_per_day = 5
        self._hobbies = []

    def get_access_level(self, repo=None):
        return f"{type(self).__name__}_level"

    def validate_content_policy(self, content_data: dict) -> bool:
        return True

    # KRİTİK DEĞİŞİKLİK: (self, repo=None) parametresini ekledik
    def get_channel_statistics(self, repo=None) -> dict:
        """
        Modül 2'den canlı veri çekerek kanal istatistiklerini hesaplar.
        """
        print(f"DEBUG: {self.name} istatistikleri hesaplanıyor, repo geldi mi?: {repo is not None}")
        # Eğer dışarıdan bir repo gönderilmediyse, yeni bir tane oluştur (Failsafe)
        if repo is None:
            from app.modules.module_2.repository import VideoRepository
            repo = VideoRepository()

        # Artık videoların kayıtlı olduğu GERÇEK repo üzerinden arama yapıyoruz
        my_videos = repo.find_by_channel(self.channel_id)

        # Videoların gelir puanlarını toplayalım
        total_potential = sum([v.calculate_monetization_potential() for v in my_videos])

        # Yayınlanmış videoların sayısını bulalım
        from app.modules.module_2.base import VideoStatus
        published_count = len([v for v in my_videos if v.status == VideoStatus.PUBLISHED])

        return {
            "kanal_id": self.channel_id,
            "abone_sayisi": self.subscriber_count,
            "toplam_video": len(my_videos),
            "yayinlanan_video": published_count,
            "toplam_gelir_potansiyeli": round(total_potential, 2),
            "erisim": self.get_access_level()
        }

    @property
    def max_videos_per_day(self):
        return self._max_videos_per_day

    @max_videos_per_day.setter
    def max_videos_per_day(self, value):
        self._max_videos_per_day = value

    def add_hobby(self, hobby):
        self._hobbies.append(hobby)
        return True

    def get_hobbies(self):
        return self._hobbies

    @staticmethod
    def get_recommended_categories():
        return ["vlog", "lifestyle", "gaming"]

    @classmethod
    def create_default_personal_channel(cls, owner_id, owner_name):
        return cls(f"personal_{owner_id}", f"{owner_name}'s Channel", "Default description", owner_id)
    def __init__(self, channel_id, name, description, owner_id):
        if len(name) < 5:
            raise InvalidNameError(f"Channel name '{name}' is too short")
        super().__init__(channel_id, name, description, owner_id, ChannelType.PERSONAL)
        self._max_videos_per_day = 5
        self._hobbies = []

    def get_access_level(self,repo=None):
        return f"{type(self).__name__}_level"

    def validate_content_policy(self, content_data: dict) -> bool:
        return True

    def get_channel_statistics(self) -> dict:
        """
        Modül 2'den canlı veri çekerek kanal istatistiklerini hesaplar.
        """
        # Modül 2'deki veritabanı (Repo) sınıfını metod içinde import ediyoruz
        from app.modules.module_2.repository import VideoRepository

        # Arkadaşının repo'sunu oluşturuyoruz
        repo = VideoRepository()

        # Bu kanala ait videoları repo üzerinden buluyoruz (Modül 2'nin gücü)
        my_videos = repo.find_by_channel(self.channel_id)

        # Videoların gelir puanlarını toplayalım
        total_potential = sum([v.calculate_monetization_potential() for v in my_videos])

        # Yayınlanmış videoların sayısını bulalım
        from app.modules.module_2.base import VideoStatus
        published_count = len([v for v in my_videos if v.status == VideoStatus.PUBLISHED])

        return {
            "kanal_id": self.channel_id,
            "abone_sayisi": self.subscriber_count,
            "toplam_video": len(my_videos),  # Canlı veri
            "yayinlanan_video": published_count,  # Canlı veri
            "toplam_gelir_potansiyeli": round(total_potential, 2),  # Modül 2'den hesaplanan veri
            "erisim": self.get_access_level()
        }

    @property
    def max_videos_per_day(self):
        return self._max_videos_per_day

    @max_videos_per_day.setter
    def max_videos_per_day(self, value):
        self._max_videos_per_day = value

    def add_hobby(self, hobby):
        self._hobbies.append(hobby)
        return True

    def get_hobbies(self):
        return self._hobbies

    @staticmethod
    def get_recommended_categories():
        return ["vlog", "lifestyle", "gaming"]

    @classmethod
    def create_default_personal_channel(cls, owner_id, owner_name):
        return cls(f"personal_{owner_id}", f"{owner_name}'s Channel", "Default description", owner_id)


class BrandChannel(BaseChannel):

    def __init__(self, channel_id, name, description, owner_id):
        super().__init__(channel_id, name, description, owner_id, ChannelType.BRAND)
        self.brand_verified = False
        self.company_name = ""
        self.marketing_budget = 0.0
        self.industry = ""
        self.target_audience = []

    def set_industry(self, industry):
        self.industry = industry
        return True

    def validate_content_policy(self, content_data: dict) -> bool:
        # Reklam politikasına uygunluk kontrolü (simülasyon)
        return True

    # app/modules/module_1/implementations.py içerisinde

    # Eski hali: def get_channel_statistics(self):
    # Yeni hali:
    def get_channel_statistics(self, repo=None):  # repo=None eklendi
        from app.modules.module_2.base import VideoStatus

        if repo:
            my_videos = repo.find_by_channel(self.channel_id)
            total_potential = sum([v.calculate_monetization_potential() for v in my_videos])
            published_count = len([v for v in my_videos if v.status == VideoStatus.PUBLISHED])
            video_len = len(my_videos)
        else:
            total_potential = 0
            published_count = 0
            video_len = 0

        return {
            "kanal_id": self.channel_id,
            "toplam_video": video_len,
            "yayinlanan_video": published_count,
            "toplam_gelir_potansiyeli": round(total_potential, 2)
        }

    def add_target_audience(self, audience):
        self.target_audience.append(audience)
        return True

    @staticmethod
    def get_valid_industries():
        return ["technology", "fashion", "food", "automotive"]

    @staticmethod
    def calculate_campaign_roi(cost, revenue):
        return ((revenue - cost) / cost) * 100

    @classmethod
    def create_verified_brand_channel(cls, owner_id, company_name, email):
        channel = cls(f"brand_{owner_id}", company_name, f"Official channel for {company_name}", owner_id)
        channel.brand_verified = True
        channel.company_name = company_name
        return channel

    def get_access_level(self):
        return "brand_corporate"


class KidsChannel(BaseChannel):

    def __init__(self, channel_id, name, description, owner_id):
        super().__init__(channel_id, name, description, owner_id, ChannelType.KIDS)
        self.parental_control_enabled = True
        self.content_rating = "G"
        self.min_age = 3
        self.max_age = 12
        self.educators = []

    def set_age_range(self, min_age, max_age):
        self.min_age = min_age
        self.max_age = max_age
        return True

    def get_age_range(self):
        return (self.min_age, self.max_age)

    def add_approved_educator(self, educator):
        self.educators.append(educator)
        return True

    def is_content_appropriate(self, rating, tags):
        # Basic check
        if self.content_rating == "G" and rating != "G":
            return False
        return True

    @staticmethod
    def get_valid_content_categories():
        return ["education", "cartoons", "science", "music"]

    @staticmethod
    def get_age_appropriate_screen_time(age):
        if age < 2: return 0
        if age < 5: return 60
        return 120

    @classmethod
    def create_educational_kids_channel(cls, owner_id, subject, age_range):
        channel = cls(f"kids_{owner_id}", f"Kids {subject}", f"Educational channel about {subject}", owner_id)
        channel.set_age_range(age_range[0], age_range[1])
        return channel

    def validate_content_policy(self, content_data: dict) -> bool:
        # Çocuklar için sadece 'G' reytingli içeriklere izin ver
        return content_data.get("rating") == "G" if "rating" in content_data else True

    def get_channel_statistics(self,repo=None) -> dict:
        return {
            "tip": "Cocuk",
            "ebeveyn_kontrolu": self.parental_control_enabled,
            "yas_araligi": self.get_age_range()}

    def get_access_level(self):
        return "kids_safe"
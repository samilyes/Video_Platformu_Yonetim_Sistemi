from .base import BaseChannel, ChannelType ,BaseUser , UserRole #UserRole silindi
from typing import List

# --- Exceptions ---
class InvalidNameError(Exception): pass


class ChannelLimitReachedError(Exception): pass


class InvalidAgeRangeError(Exception): pass


class ContentNotAllowedError(Exception): pass


class BrandVerificationError(Exception): pass


class SubscriptionRequiredError(Exception): pass


class AdminUser(BaseUser):
    def __init__(self, user_id, username, email, password, role=UserRole.ADMIN):
        super().__init__(user_id, username, email, password, role)

    def get_permissions(self) -> List[str]:
        return ["delete_user", "suspend_channel", "edit_any_content", "view_analytics"]

class ContentCreatorUser(BaseUser):
    def __init__(self, user_id, username, email, password, role=UserRole.CONTENT_CREATOR):
        super().__init__(user_id, username, email, password, role)

    def get_permissions(self) -> List[str]:
        return ["create_video", "edit_own_channel", "view_own_analytics"]

class ViewerUser(BaseUser):
    def __init__(self, user_id, username, email, password, role=UserRole.VIEWER):
        super().__init__(user_id, username, email, password, role)

    def get_permissions(self) -> List[str]:
        return ["view_video", "subscribe", "comment"]


# --- PersonalChannel ---
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

    def get_channel_statistics(self, repo=None) -> dict:
        # Modül 2'den canlı veri çekerek kanal istatistiklerini hesaplartır
        if repo is None:
            from app.modules.module_2.repository import VideoRepository
            repo = VideoRepository()

        my_videos = repo.find_by_channel(self.channel_id)
        total_potential = sum([v.calculate_monetization_potential() for v in my_videos])

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


# --- BrandChannel ---
class BrandChannel(BaseChannel):
    def __init__(self, channel_id, name, description, owner_id):
        super().__init__(channel_id, name, description, owner_id, ChannelType.BRAND)
        self.brand_verified = False
        self._company_name = ""  # Kapsüllendi
        self._marketing_budget = 0.0  # Kapsüllendi
        self.industry = ""
        self.target_audience = []

    @property
    def marketing_budget(self):
        return self._marketing_budget

    @marketing_budget.setter
    def marketing_budget(self, value):
        if value < 0:
            print("Sistem >> Uyarı: Bütçe negatif olamaz. İşlem reddedildi.")
            return
        self._marketing_budget = value

    @property
    def company_name(self):
        return self._company_name

    @company_name.setter
    def company_name(self, value):
        if not value or len(value.strip()) < 2:
            print("Sistem >> Uyarı: Geçersiz şirket adı.")
            return
        self._company_name = value

    def set_industry(self, industry):
        self.industry = industry
        return True

    def validate_content_policy(self, content_data: dict) -> bool:
        return True

    def get_channel_statistics(self, repo=None):
        from app.modules.module_2.base import VideoStatus
        if repo:
            my_videos = repo.find_by_channel(self.channel_id)
            total_potential = sum([v.calculate_monetization_potential() for v in my_videos])
            published_count = len([v for v in my_videos if v.status == VideoStatus.PUBLISHED])
            video_len = len(my_videos)
        else:
            total_potential = published_count = video_len = 0

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
    def create_verified_brand_channel(cls, owner_id, company_name): #email silindi
        channel = cls(f"brand_{owner_id}", company_name, f"Official channel for {company_name}", owner_id)
        channel.brand_verified = True
        channel.company_name = company_name
        return channel

    def get_access_level(self):
        return "brand_corporate"


# --- KidsChannel ---
class KidsChannel(BaseChannel):
    def __init__(self, channel_id, name, description, owner_id):
        super().__init__(channel_id, name, description, owner_id, ChannelType.KIDS)
        self.parental_control_enabled = True
        self._content_rating = "G"  # Kapsüllendi
        self._min_age = 3  # Kapsüllendi
        self._max_age = 12  # Kapsüllendi
        self.educators = []

    @property
    def min_age(self):
        return self._min_age

    @min_age.setter
    def min_age(self, value):
        if value < 0: raise InvalidAgeRangeError("Yaş negatif olamaz.")
        self._min_age = value

    @property
    def max_age(self):
        return self._max_age

    @max_age.setter
    def max_age(self, value):
        if value < self._min_age: raise InvalidAgeRangeError("Maksimum yaş minimumdan küçük olamaz.")
        self._max_age = value

    @property
    def content_rating(self):
        return self._content_rating

    @content_rating.setter
    def content_rating(self, value):
        valid_ratings = ["G", "PG"]
        if value not in valid_ratings:
            raise ContentNotAllowedError(f"Çocuk kanalı için {value} reytingi uygun değil!")
        self._content_rating = value

    @staticmethod
    def get_age_appropriate_screen_time(age):
        # Yaşa göre önerilen günlük maksimum ekran süresini (dakika) döndürür.
        if age < 2:
            return 0
        if age < 5:
            return 60
        return 120

    @classmethod
    def create_educational_kids_channel(cls, owner_id, subject, age_range):
        # Eğitici bir çocuk kanalı oluşturmak için kullanılan yardımcı sınıf metodu.
        channel_id = f"kids_edu_{owner_id}"
        name = f"Kids Learning - {subject.capitalize()}"
        description = f"Educational content for kids focusing on {subject}."

        # Yeni kanalı oluşturuyoruz
        channel = cls(channel_id, name, description, owner_id)
        # Yaş aralığını set ediyoruz
        channel.set_age_range(age_range[0], age_range[1])

        return channel

    def set_age_range(self, min_age, max_age):
        self.min_age = min_age
        self.max_age = max_age
        return True

    def get_age_range(self):
        return self._min_age, self._max_age # parantezler kladırıldıki gereksiz

    def add_approved_educator(self, educator):
        self.educators.append(educator)
        return True

    def is_content_appropriate(self, rating): #tags silindi
        if self.content_rating == "G" and rating != "G":
            return False
        return True

    @staticmethod
    def get_valid_content_categories():
        return ["education", "cartoons", "science", "music"]

    def validate_content_policy(self, content_data: dict) -> bool:
        return content_data.get("rating") == "G" if "rating" in content_data else True

    def get_channel_statistics(self, repo=None) -> dict:
        return {
            "tip": "Cocuk",
            "ebeveyn_kontrolu": self.parental_control_enabled,
            "yas_araligi": self.get_age_range()
        }

    def get_access_level(self):
        return "kids_safe"
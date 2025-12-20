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

    def get_access_level(self):
        return f"{type(self).__name__}_level"

    def validate_content_policy(self, content_data: dict) -> bool:
        return True

    def get_channel_statistics(self) -> dict:
        return {
            "channel_id": self.channel_id,
            "subscribers": self.subscriber_count,
            "videos": self.video_count
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

    def get_channel_statistics(self) -> dict:
        return {
            "tip": "Marka",
            "butce": self.marketing_budget,
            "etkilesim": self.subscriber_count * 1.5
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

    def get_channel_statistics(self) -> dict:
        return {
            "tip": "Cocuk",
            "ebeveyn_kontrolu": self.parental_control_enabled,
            "yas_araligi": self.get_age_range()}

    def get_access_level(self):
        return "kids_safe"
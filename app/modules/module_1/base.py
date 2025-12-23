from enum import Enum
from datetime import datetime
from typing import List
from abc import ABC, abstractmethod


class UserRole(Enum):
    ADMIN = "admin"
    CONTENT_CREATOR = "content_creator"
    VIEWER = "viewer"


class BaseUser(ABC):
    def __init__(self, user_id, username, email, password, role):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password = password
        self.role = role
        self.created_at = datetime.now()
        self.is_active = True

    @abstractmethod
    def get_permissions(self) -> List[str]:
        # Her kullanıcı alt sınıfı kendi izin listesini döndürmelidir
        pass

    @property
    def mail(self):
        return getattr(self, "_email", None)

    @mail.setter
    def mail(self, value):
        if "@" not in value:
            raise ValueError(f"E mail geçersiz ! ")
        self._email = value

    @property
    def password(self):
        return getattr(self, "_password", None)

    # base.py
    @password.setter
    def password(self, value):
        if len(value) < 8:
            raise ValueError("Şifre en az 8 karakter olmalıdır!")
        self._password = value




class ChannelType(Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    PREMIUM = "premium"
    PERSONAL = "personal"
    BRAND = "brand"
    KIDS = "kids"


class ChannelStatus(Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"


class UserNotFoundException(Exception):
    pass

class ChannelNotFoundException(Exception):
    pass

class DuplicateUserException(Exception):
    pass

class DuplicateChannelException(Exception):
    pass



class AdminUser(BaseUser):
    def __init__(self, user_id, username, email, password, role=UserRole.ADMIN):
        super().__init__(user_id, username, email, password, role)

    def get_permissions(self) -> List[str]:
        return ["manage_users", "delete_video", "edit_channels", "view_analytics"]

class ContentCreatorUser(BaseUser):
    def __init__(self, user_id, username, email, password, role=UserRole.CONTENT_CREATOR):
        super().__init__(user_id, username, email, password, role)
    def get_permissions(self) -> List[str]:
        return ["upload_video", "edit_own_channel", "view_analytics"]

class ViewerUser(BaseUser):
    def __init__(self, user_id, username, email, password, role=UserRole.VIEWER):
        super().__init__(user_id, username, email, password, role)

    def get_permissions(self) -> List[str]:
        return ["view_video", "comment", "subscribe"]


class BaseChannel(ABC):
    def __init__(self, channel_id, name, description, owner_id, channel_type, category="other"):
        self.channel_id = channel_id
        self.name = name
        self.description = description
        self.owner_id = owner_id
        self.channel_type = channel_type
        self.category = category
        self.status = ChannelStatus.ACTIVE
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.subscriber_count = 0
        self.video_count = 0
        self.moderators = set()
        self.tags = []



    @abstractmethod
    def get_access_level(self) -> str:
        pass

    @abstractmethod
    def validate_content_policy(self, content_data: dict) -> bool:
        # icerik politikasi uyum denetimi
        pass

    @abstractmethod
    def get_channel_statistics(self) -> dict:
        # Kanala istatistik ozetini return etme
        pass

    def change_status(self, new_status: ChannelStatus):
        # durum degisikligi
        self.status = new_status
        self.updated_at = datetime.now()
        print(f"System >> Kanal {self.channel_id} durumu {new_status.value} olarak degistirildi")


    def can_user_access(self, user_id, role):
        # kullanici erişebilir mi
        if user_id == self.owner_id:
            return True
        if role == UserRole.ADMIN:
            return True
        return self.status == ChannelStatus.ACTIVE

    def update_info(self, description=None):
        if description:
            self.description = description
        self.updated_at = datetime.now()
        # BaseChannel sınıfının içine ekle

    def increment_video_count(self):
        # Video başarıyla yüklendiği için sayaç artır
        self.video_count += 1
        self.updated_at = datetime.now()


class PublicChannel(BaseChannel):
    def __init__(self, channel_id, name, description, owner_id, channel_type=ChannelType.PUBLIC):
        super().__init__(channel_id, name, description, owner_id, channel_type)


class PrivateChannel(BaseChannel):
    def __init__(self, channel_id, name, description, owner_id, channel_type=ChannelType.PRIVATE):
        super().__init__(channel_id, name, description, owner_id, channel_type)


class PremiumChannel(BaseChannel):
    def __init__(self, channel_id, name, description, owner_id, channel_type=ChannelType.PREMIUM):
        super().__init__(channel_id, name, description, owner_id, channel_type)
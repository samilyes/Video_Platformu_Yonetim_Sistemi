from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict
from dataclasses import dataclass, field


class UserRole(Enum):
    # roller
    ADMIN = "admin"
    MODERATOR = "moderator"
    CONTENT_CREATOR = "content_creator"
    VIEWER = "viewer"


class ChannelStatus(Enum):
    # Kanal durumu
    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"
    DELETED = "deleted"


class ChannelType(Enum):
    # Kanal tipleri
    PUBLIC = "public"
    PRIVATE = "private"
    PREMIUM = "premium"


class NotificationType(Enum):
    # Bildirim tipleri
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


# Abstract Base Classes
class BaseUser(ABC):
    # Temel kullanıcı abstract sınıfı

    def __init__(self, user_id: str, username: str, email: str, password_hash: str, role: UserRole):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.is_active = True
        self.profile_picture: Optional[str] = None
        self.bio: Optional[str] = None
        self.channels: List[str] = []

    @abstractmethod
    def get_permissions(self) -> List[str]:
        # Kullanıcının yetkilerini döndür
        pass

    @abstractmethod
    def can_create_channel(self) -> bool:
        # Kullanıcı kanal oluşturabilir mi
        pass

    def update_profile(self, **kwargs):
        # Kullanıcı profil bilgilerini güncelle

        allowed_fields = ['bio', 'profile_picture']
        for key, value in kwargs.items():
            if key in allowed_fields:
                setattr(self, key, value)
        self.updated_at = datetime.now()

    def add_channel(self, channel_id: str):
        # Kullanıcıya kanal ekle
        if channel_id not in self.channels:
            self.channels.append(channel_id)

    @classmethod
    def validate_username(cls, username: str) -> bool:
        # Kullanıcı adı validasyonu
        return len(username) >= 3 and username.replace('_', '').isalnum()

    @classmethod
    def validate_email(cls, email: str) -> bool:
        # Email validasyonu
        return "@" in email and "." in email.split("@")[1]

    @staticmethod
    def generate_display_name(first_name: str, last_name: str) -> str:
        # Display name oluştur
        return f"{first_name} {last_name}".strip()

    @staticmethod
    def calculate_account_age(created_at: datetime) -> int:
        # Hesap yaşını gün olarak hesapla
        return (datetime.now() - created_at).days


class BaseChannel(ABC):
    # kanal abstract sınıfı

    def __init__(self, channel_id: str, name: str, description: str, owner_id: str, channel_type: ChannelType):
        self.channel_id = channel_id
        self.name = name
        self.description = description
        self.owner_id = owner_id
        self.channel_type = channel_type
        self.status = ChannelStatus.PENDING
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.subscriber_count = 0
        self.video_count = 0
        self.banner_image: Optional[str] = None
        self.category: Optional[str] = None
        self.tags: List[str] = []
        self.moderators: List[str] = []

    # Kanalın erişim seviyesini döndür
    @abstractmethod
    def get_access_level(self) -> str:
        pass

    # Kullanıcı kanala erişebilir mi?
    @abstractmethod
    def can_user_access(self, user_id: str, user_role: UserRole) -> bool:
        pass

    def update_info(self, **kwargs):
        # Kanal bilgilerini güncelle
        allowed_fields = ['name', 'description', 'banner_image', 'category']
        for key, value in kwargs.items():
            if key in allowed_fields:
                setattr(self, key, value)
        self.updated_at = datetime.now()

    def add_moderator(self, user_id: str):
        # Kanala moderatör ekleletir
        if user_id not in self.moderators and user_id != self.owner_id:
            self.moderators.append(user_id)

    @classmethod
    def validate_channel_name(cls, name: str) -> bool:
        # Kanal adı validasyonu
        return 2 <= len(name) <= 50

    @classmethod
    def generate_channel_url(cls, channel_name: str) -> str:
        # Kanal URL si oluşturur
        clean_name = channel_name.lower().replace(" ", "-")
        return f"/channel/{clean_name}"
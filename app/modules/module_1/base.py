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

    def __init__(self, user_id: str, username: str, email: str, password: str, role: UserRole):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password = password
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

    @staticmethod
    def calculate_engagement_rate(views: int, subscribers: int) -> float:
        # Etkileşim oranını hesaplatır
        if subscribers == 0:
            return 0.0
        return (views / subscribers) * 100

    @staticmethod
    def format_subscriber_count(count: int) -> str:
        # Abone sayısını formatla
        if count >= 1000000:
            return f"{count / 1000000:.1f}M"
        elif count >= 1000:
            return f"{count / 1000:.1f}K"
        return str(count)


class BaseNotification(ABC):
    # Temel bildirim abstract sınıfı

    def __init__(self, notification_id: str, user_id: str, title: str, message: str,
                 notification_type: NotificationType):
        self.notification_id = notification_id
        self.user_id = user_id
        self.title = title
        self.message = message
        self.notification_type = notification_type
        self.created_at = datetime.now()
        self.is_read = False
        self.sent_at: Optional[datetime] = None

    @abstractmethod
    def send(self) -> bool:
        # Bildirim gönder
        pass

    @abstractmethod
    def get_delivery_method(self) -> str:
        # Teslimat yöntemini döndür
        pass

    def mark_as_read(self):
        # Bildirim okundu işaretle
        self.is_read = True

    def mark_as_sent(self):
        # Bildirim gönderildi işaretle
        self.sent_at = datetime.now()

    @classmethod
    def create_welcome_notification(cls, user_id: str, username: str):
        # Bildirim --> Hoş geldin - EmailNotification döndürür
        # Bu metot concrete sınıflardan çağrılmalı
        return {
            'notification_id': f"welcome_{user_id}",
            'user_id': user_id,
            'title': "Hoş Geldiniz!",
            'message': f"Merhaba {username}, platformumuza hoş geldiniz!",
            'notification_type': NotificationType.EMAIL
        }

    @classmethod
    def create_channel_notification(cls, user_id: str, channel_name: str):
        # Kanal bildirimi oluştur - PushNotification döndürür
        return {
            'notification_id': f"channel_{user_id}",
            'user_id': user_id,
            'title': "Yeni Kanal",
            'message': f"'{channel_name}' kanalınız oluşturuldu!",
            'notification_type': NotificationType.PUSH
        }

    @staticmethod
    def truncate_message(message: str, max_length: int = 100) -> str:
        # Mesajı kısalt
        if len(message) <= max_length:
            return message
        return message[:max_length - 3] + "..."

    @staticmethod
    def format_timestamp(timestamp: datetime) -> str:
        # Zaman birimini formatlar
        return timestamp.strftime("%d.%m.%Y %H:%M")


# Concrete User Classes
class AdminUser(BaseUser):
    # Admin kullanıcı sınıfı

    def get_permissions(self) -> List[str]:
        # Admin superuser dır
        return [
            "create_channel", "delete_channel", "suspend_channel",
            "manage_users", "view_analytics", "system_settings",
            "moderate_content", "approve_channels"
        ]

    def can_create_channel(self) -> bool:
        # Admin kanal oluşturma yetkisi
        return True

# askıya alma
    def suspend_user(self, user_id: str) -> bool:
        return True

# Sistem analizi
    def view_system_analytics(self) -> Dict:
        return {
            "total_users": 0,
            "total_channels": 0,
            "system_health": "good"
        }


# İçerik üreticisi kullanıcı sınıfı
class ContentCreatorUser(BaseUser):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.monetization_enabled = False
        self.total_earnings = 0.0

# yetkileri
    def get_permissions(self) -> List[str]:
        return [
            "create_channel", "upload_video", "manage_own_channels",
            "view_analytics", "monetize_content"
        ]

# kanal oluşturabilir yetkisi
    def can_create_channel(self) -> bool:
        return True

# Para kazanmayı etkinleştirme
    def enable_monetization(self) -> bool:
        if len(self.channels) > 0:
            self.monetization_enabled = True
            return True
        return False

# Kazanç hesabı
    def calculate_earnings(self, views: int, cpm: float = 2.0) -> float:
        if self.monetization_enabled:
            earnings = (views / 1000) * cpm
            self.total_earnings += earnings
            return earnings
        return 0.0

# İzleyici kullanıcı sınıfı
class ViewerUser(BaseUser):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subscriptions: List[str] = []
        self.watch_history: List[str] = []
        self.preferences: Dict = {}

# izleyici yetkilerri
    def get_permissions(self) -> List[str]:
        return [
            "watch_videos", "subscribe_channels", "comment_videos",
            "create_playlists", "rate_videos"
        ]

# kanal oluşturamaz
    def can_create_channel(self) -> bool:
        return False

# abone olma durumu
    def subscribe_to_channel(self, channel_id: str) -> bool:
        if channel_id not in self.subscriptions:
            self.subscriptions.append(channel_id)
            return True
        return False

# izleme geçmişine ekler
    def add_to_watch_history(self, video_id: str):
        if video_id not in self.watch_history:
            self.watch_history.append(video_id)
            if len(self.watch_history) > 100:
                self.watch_history.pop(0)


# Herkese açık kanal sınıfı
class PublicChannel(BaseChannel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel_type = ChannelType.PUBLIC
        self.featured = False

# erişim
    def get_access_level(self) -> str:
        return "public"

# herkes erişebilir
    def can_user_access(self, user_id: str, user_role: UserRole) -> bool:
        return True

# öne çkarmak
    def set_featured(self, featured: bool = True):
        self.featured = featured

# Herkese açık metrikleri döndür
    def get_public_metrics(self) -> Dict:
        return {
            "subscriber_count": self.subscriber_count,
            "video_count": self.video_count,
            "featured": self.featured
        }


# özel kanal ----------------------------
class PrivateChannel(BaseChannel):


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel_type = ChannelType.PRIVATE
        self.invited_users: List[str] = []

# erişim private
    def get_access_level(self) -> str:
        return "private"

# Sadece davetli kullanıcılar ve sahip erişebilir
    def can_user_access(self, user_id: str, user_role: UserRole) -> bool:
        return (user_id == self.owner_id or
                user_id in self.invited_users or
                user_role == UserRole.ADMIN)

# kullanıcı daveti
    def invite_user(self, user_id: str) -> bool:

        if user_id not in self.invited_users:
            self.invited_users.append(user_id)
            return True
        return False

# daveti kaldırma
    def remove_invitation(self, user_id: str) -> bool:
        if user_id in self.invited_users:
            self.invited_users.remove(user_id)
            return True
        return False

# katıl kanal
class PremiumChannel(BaseChannel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel_type = ChannelType.PREMIUM
        self.subscription_price = 9.99
        self.premium_subscribers: List[str] = []

# erişim
    def get_access_level(self) -> str:
        return "premium"

# kimler erişebilir (katıl)
    def can_user_access(self, user_id: str, user_role: UserRole) -> bool:
        return (user_id == self.owner_id or
                user_id in self.premium_subscribers or
                user_role == UserRole.ADMIN)

# katıl abonesi ekleme
    def add_premium_subscriber(self, user_id: str) -> bool:
        if user_id not in self.premium_subscribers:
            self.premium_subscribers.append(user_id)
            return True
        return False

# gelir hesabı
    def calculate_monthly_revenue(self) -> float:
        return len(self.premium_subscribers) * self.subscription_price

# Email bildirimi ------------------------------------------------------------------------------------------
class EmailNotification(BaseNotification):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.notification_type = NotificationType.EMAIL
        self.email_address: Optional[str] = None

# gönder e-mail
    def send(self) -> bool:
        if self.email_address:
            # Email gönderme simülasyonu
            print(f"Email gönderiliyor: {self.email_address}")
            print(f"Konu: {self.title}")
            print(f"İçerik: {self.message}")
            self.mark_as_sent()
            return True
        return False

# teslimat yöntemi
    def get_delivery_method(self) -> str:
        return "SMTP Server"

# adresini ayarlama
    def set_email_address(self, email: str):
        self.email_address = email


# sms bildirim sınıfı -----------------------------------------------------------------------------------
class SMSNotification(BaseNotification):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.notification_type = NotificationType.SMS
        self.phone_number: Optional[str] = None

# sms göndrme
    def send(self) -> bool:
        if self.phone_number:
            # SMS gönderme simülasyonu
            short_message = self.truncate_message(self.message, 160)
            print(f"SMS gönderiliyor: {self.phone_number}")
            print(f"Mesaj: {short_message}")
            self.mark_as_sent()
            return True
        return False

# teslimat yöntemi
    def get_delivery_method(self) -> str:
        return "SMS Gateway"

# telefon numarası ayarlama
    def set_phone_number(self, phone: str):
        self.phone_number = phone

# anlık bildirim sınıfı tanımlanması
class PushNotification(BaseNotification):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.notification_type = NotificationType.PUSH
        self.device_token: Optional[str] = None
        self.priority = "normal"

# anlık gönderme
    def send(self) -> bool:
        if self.device_token:
            # anlık bildirim gönderme simülasyonu
            print(f"Push bildirimi gönderiliyor: {self.device_token}")
            print(f"Başlık: {self.title}")
            print(f"Mesaj: {self.message}")
            print(f"Öncelik: {self.priority}")
            self.mark_as_sent()
            return True
        return False

# teslimat yöntemi
    def get_delivery_method(self) -> str:
        return "Firebase Cloud Messaging"

# cihaz token ayrlama
    def set_device_token(self, token: str):
        self.device_token = token

# öncelik durumu
    def set_high_priority(self):
        self.priority = "high"


# veri class'ı
@dataclass
class UserChannelSubscription:
    # Kullanıcı-Kanal abonelik ilişkisi
    user_id: str
    channel_id: str
    subscribed_at: datetime = field(default_factory=datetime.now)
    notifications_enabled: bool = True

# açıp-kapatma
    def toggle_notifications(self):
        self.notifications_enabled = not self.notifications_enabled


# Exception class ı
class BaseException(Exception):
    pass


# user not found
class UserNotFoundException(BaseException):
    pass


# channel not found
class ChannelNotFoundException(BaseException):
    pass


# user exists
class DuplicateUserException(BaseException):
    pass

# channel exists
class DuplicateChannelException(BaseException):
    pass

# yetkisiz erişim
class UnauthorizedAccessException(BaseException):
    pass

# yetersiz yetki
class InsufficientPermissionsException(BaseException):
    pass
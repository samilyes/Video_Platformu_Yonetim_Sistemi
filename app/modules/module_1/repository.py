import json
import os
from typing import List, Optional, Dict, Union
from datetime import datetime
from .base import (
    BaseUser, BaseChannel, UserRole, ChannelStatus, ChannelType,
    AdminUser, ContentCreatorUser, ViewerUser,
    PublicChannel, PrivateChannel, PremiumChannel,
    UserChannelSubscription,
    UserNotFoundException, ChannelNotFoundException,
    DuplicateUserException, DuplicateChannelException
)

# Kullanıcı ve Kanal verilerinin saklanması ve erişimi için repository sınıfları

class BaseRepository:
    # Temel repository

    def __init__(self, data_file: str):
        self.data_file = data_file
        self.data = self._load_data()

    def _load_data(self) -> Dict:
        # Dosyadan veri yükle
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}

    def _save_data(self):
        # Veriyi dosyaya kaydet
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2, default=str)

    def backup_data(self, backup_path: str) -> bool:
        # Veriyi yedekle
        try:
            import shutil
            shutil.copy2(self.data_file, backup_path)
            return True
        except Exception:
            return False

    @classmethod
    def validate_data_structure(cls, data: Dict) -> bool:
        # Veri yapısını doğrula
        return isinstance(data, dict)

    @staticmethod
    def generate_backup_filename(original_file: str) -> str:
        # Yedek dosya adı oluştur
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name, ext = os.path.splitext(original_file)
        return f"{name}_backup_{timestamp}{ext}"
# ----------------------------------------------------------------------------> 5.gun
class UserRepository(BaseRepository):
    # Kullanıcı veri erişim sınıfı

    def __init__(self, data_file: str = "data/users.json"):
        super().__init__(data_file)
        if 'users' not in self.data:
            self.data['users'] = {}
        if 'subscriptions' not in self.data:
            self.data['subscriptions'] = {}

    def _user_data_to_object(self, user_data: Dict) -> BaseUser:
        # Veri dict'ini user objesine çevir
        role = UserRole(user_data['role'])

        # Role göre doğru sınıfı oluştur
        if role == UserRole.ADMIN:
            user = AdminUser(
                user_data['user_id'],
                user_data['username'],
                user_data['email'],
                user_data['password_hash'],
                role
            )
        elif role == UserRole.CONTENT_CREATOR:
            user = ContentCreatorUser(
                user_data['user_id'],
                user_data['username'],
                user_data['email'],
                user_data['password_hash'],
                role
            )
            # ContentCreator özel alanları
            if 'monetization_enabled' in user_data:
                user.monetization_enabled = user_data['monetization_enabled']
            if 'total_earnings' in user_data:
                user.total_earnings = user_data['total_earnings']
        else:
            user = ViewerUser(
                user_data['user_id'],
                user_data['username'],
                user_data['email'],
                user_data['password_hash'],
                role
            )
            # Viewer özel alanları
            if 'subscriptions' in user_data:
                user.subscriptions = user_data['subscriptions']
            if 'watch_history' in user_data:
                user.watch_history = user_data['watch_history']
            if 'preferences' in user_data:
                user.preferences = user_data['preferences']

        # Ortak alanları ayarla
        user.created_at = datetime.fromisoformat(user_data['created_at'])
        user.updated_at = datetime.fromisoformat(user_data['updated_at'])
        user.is_active = user_data['is_active']
        user.profile_picture = user_data.get('profile_picture')
        user.bio = user_data.get('bio')
        user.channels = user_data.get('channels', [])

        return user

    def _user_object_to_data(self, user: BaseUser) -> Dict:
        """User objesini veri dict'ine çevir"""
        data = {
            'user_id': user.user_id,
            'username': user.username,
            'email': user.email,
            'password_hash': user.password_hash,
            'role': user.role.value,
            'created_at': user.created_at.isoformat(),
            'updated_at': user.updated_at.isoformat(),
            'is_active': user.is_active,
            'profile_picture': user.profile_picture,
            'bio': user.bio,
            'channels': user.channels
        }

        # Özel alanları ekle
        if isinstance(user, ContentCreatorUser):
            data.update({
                'monetization_enabled': user.monetization_enabled,
                'total_earnings': user.total_earnings
            })
        elif isinstance(user, ViewerUser):
            data.update({
                'subscriptions': user.subscriptions,
                'watch_history': user.watch_history,
                'preferences': user.preferences
            })

        return data

    def create_user(self, user: BaseUser) -> BaseUser:
        """Yeni kullanıcı oluştur"""
        if user.user_id in self.data['users']:
            raise DuplicateUserException(f"Kullanıcı ID {user.user_id} zaten mevcut")

        # Email kontrolü - sadece mevcut veriler varsa
        if self.data['users']:
            for existing_user_data in self.data['users'].values():
                if existing_user_data.get('email') == user.email:
                    raise DuplicateUserException(f"Email {user.email} zaten kullanılıyor")

            # Username kontrolü - sadece mevcut veriler varsa
            for existing_user_data in self.data['users'].values():
                if existing_user_data.get('username') == user.username:
                    raise DuplicateUserException(f"Kullanıcı adı {user.username} zaten kullanılıyor")

        self.data['users'][user.user_id] = self._user_object_to_data(user)
        self._save_data()
        return user

    def get_user_by_id(self, user_id: str) -> BaseUser:
        """ID ile kullanıcı getir"""
        if user_id not in self.data['users']:
            raise UserNotFoundException(f"Kullanıcı ID {user_id} bulunamadı")

        user_data = self.data['users'][user_id]
        return self._user_data_to_object(user_data)

    def get_user_by_username(self, username: str) -> BaseUser:
        """Kullanıcı adı ile kullanıcı getir"""
        for user_data in self.data['users'].values():
            if user_data['username'] == username:
                return self._user_data_to_object(user_data)
        raise UserNotFoundException(f"Kullanıcı adı '{username}' bulunamadı")

    def get_user_by_email(self, email: str) -> BaseUser:
        """Email ile kullanıcı getir"""
        for user_data in self.data['users'].values():
            if user_data['email'] == email:
                return self._user_data_to_object(user_data)
        raise UserNotFoundException(f"Email '{email}' bulunamadı")

    def update_user(self, user: BaseUser) -> BaseUser:
        """Kullanıcı bilgilerini güncelle"""
        if user.user_id not in self.data['users']:
            raise UserNotFoundException(f"Kullanıcı ID {user.user_id} bulunamadı")

        self.data['users'][user.user_id] = self._user_object_to_data(user)
        self._save_data()
        return user

# ------------------------------------------------------------------------------------> 6.gun 202 -314

        @classmethod
        def create_with_default_admin(cls, data_file: str = "users.json"):
            repo = cls(data_file)

            admin_users = repo.get_users_by_role(UserRole.ADMIN)

            if not admin_users:
                admin_user = AdminUser(
                    "admin_default", "admin", "admin@system.local",
                    "hashed_admin_password_123", UserRole.ADMIN
                )

                try:
                    repo.create_user(admin_user)
                    print(f"System: Default admin user created successfully")
                except Exception as e:
                    print(f"System: Error creating default admin: {e}")

            return repo

        @staticmethod
        def validate_username(username: str) -> bool:
            return (isinstance(username, str) and username.strip() and 3 <= len(username.strip()) <= 30)

        @staticmethod
        def validate_email(email: str) -> bool:
            return (isinstance(email, str) and email.strip() and '@' in email and '.' in email.split('@')[1])

    class ChannelRepository:
        # Kanal veri erişim sınıfı - kanal CRUD işlemleri için

        def __init__(self, data_file: str = "channels.json"):
            print(f"System: Initializing ChannelRepository with data file: {data_file}")

            self.__data_file = data_file  # Private attribute
            self.__channels = {}  # Private attribute - channel_id -> BaseChannel
            self.__owner_index = {}  # Private attribute - owner_id -> List[channel_id]
            self.__type_index = {}  # Private attribute - channel_type -> List[channel_id]
            self.__last_modified = datetime.now()  # Private attribute

            # Dosya varsa yükle
            if os.path.exists(self.__data_file):
                self._load_from_file()
            else:
                print(f"System: Data file {data_file} does not exist, starting with empty repository")
                self._initialize_empty_repository()

            print(f"System: ChannelRepository initialized with {len(self.__channels)} channels")

        def _initialize_empty_repository(self):
            # Boş repository başlat
            self.__channels = {}
            self.__owner_index = {}
            self.__type_index = {}
            self.__last_modified = datetime.now()
            print(f"System: Empty channel repository initialized")

        def _load_from_file(self):
            # Dosyadan kanalları yükle
            try:
                with open(self.__data_file, 'r', encoding='utf-8') as file:
                    data = json.load(file)

                channels_data = data.get('channels', {})
                for channel_id, channel_data in channels_data.items():
                    channel = self._deserialize_channel(channel_data)
                    if channel:
                        self.__channels[channel_id] = channel
                        self._update_indexes(channel)

                print(f"System: Successfully loaded {len(self.__channels)} channels from file")

            except Exception as e:
                print(f"System: Error loading channels from file: {e}")
                self._initialize_empty_repository()

        def _save_to_file(self):
            # Kanalları dosyaya kaydet
            try:
                channels_data = {cid: self._serialize_channel(ch) for cid, ch in self.__channels.items()}
                data = {
                    'channels': channels_data,
                    'metadata': {'last_modified': self.__last_modified.isoformat(),
                                 'total_channels': len(self.__channels)}
                }

                with open(self.__data_file, 'w', encoding='utf-8') as file:
                    json.dump(data, file, indent=2, ensure_ascii=False)

                print(f"System: Successfully saved {len(channels_data)} channels to file")

            except Exception as e:
                print(f"System: Error saving channels to file: {e}")
                raise

        def _serialize_channel(self, channel: BaseChannel) -> Dict[str, Any]:
            # Kanalı dictionary'ye çevir
            return {
                'channel_id': channel.channel_id,
                'name': channel.name,
                'description': channel.description,
                'owner_id': channel.owner_id,
                'channel_type': channel.channel_type.value,
                'status': channel.status.value,
                'created_at': channel.created_at.isoformat(),
                'updated_at': channel.updated_at.isoformat(),
                'subscriber_count': channel.subscriber_count,
                'video_count': channel.video_count,
                'moderators': list(channel.moderators),
                'tags': list(channel.tags),
                'channel_class': type(channel).__name__
            }


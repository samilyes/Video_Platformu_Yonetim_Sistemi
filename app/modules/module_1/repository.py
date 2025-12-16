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

# ------------------------------------------------------------------------------------> 6.gun
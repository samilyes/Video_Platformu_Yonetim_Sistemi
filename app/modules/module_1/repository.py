import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from base import (
    BaseUser, BaseChannel, UserRole, ChannelType, ChannelStatus,
    AdminUser, ContentCreatorUser, ViewerUser,
    PublicChannel, PrivateChannel, PremiumChannel,
    UserNotFoundException, ChannelNotFoundException,
    DuplicateUserException, DuplicateChannelException
)


class UserRepository:
    # Kullanıcı veri erişim sınıfı - kullanıcı CRUD işlemleri için

    def __init__(self, data_file: str = "users.json"):
        print(f"System: Initializing UserRepository with data file: {data_file}")

        self.__data_file = data_file  # Private attribute
        self.__users = {}  # Private attribute - user_id -> BaseUser
        self.__username_index = {}  # Private attribute - username -> user_id
        self.__email_index = {}  # Private attribute - email -> user_id
        self.__last_modified = datetime.now()  # Private attribute

        # Dosya varsa yükle
        if os.path.exists(self.__data_file):
            self._load_from_file()
        else:
            print(f"System: Data file {data_file} does not exist, starting with empty repository")
            self._initialize_empty_repository()

        print(f"System: UserRepository initialized with {len(self.__users)} users")

    def _initialize_empty_repository(self):
        # Boş repository başlat
        self.__users = {}
        self.__username_index = {}
        self.__email_index = {}
        self.__last_modified = datetime.now()
        print(f"System: Empty repository initialized")

    def _load_from_file(self):
        # Dosyadan kullanıcıları yükle
        try:
            with open(self.__data_file, 'r', encoding='utf-8') as file:
                data = json.load(file)

            users_data = data.get('users', {})
            for user_id, user_data in users_data.items():
                user = self._deserialize_user(user_data)
                if user:
                    self.__users[user_id] = user
                    self._update_indexes(user)

            print(f"System: Successfully loaded {len(self.__users)} users from file")

        except Exception as e:
            print(f"System: Error loading from file: {e}")
            self._initialize_empty_repository()

    def _save_to_file(self):
        # Kullanıcıları dosyaya kaydet
        try:
            users_data = {user_id: self._serialize_user(user) for user_id, user in self.__users.items()}
            data = {
                'users': users_data,
                'metadata': {'last_modified': self.__last_modified.isoformat(), 'total_users': len(self.__users)}
            }

            with open(self.__data_file, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)

            print(f"System: Successfully saved {len(users_data)} users to file")

        except Exception as e:
            print(f"System: Error saving to file: {e}")
            raise

    def _serialize_user(self, user: BaseUser) -> Dict[str, Any]:
        # Kullanıcıyı dictionary'ye çevir
        return {
            'user_id': user.user_id,
            'username': user.username,
            'email': user.email,
            'password_hash': user.password,
            'role': user.role.value,
            'user_type': type(user).__name__,
            'created_at': user.created_at.isoformat(),
            'is_active': user.is_active
        }

    def _deserialize_user(self, user_data: Dict[str, Any]) -> Optional[BaseUser]:
        # Dictionary'den kullanıcı oluştur
        try:
            user_type = user_data.get('user_type', 'ViewerUser')
            role = UserRole(user_data['role'])

            user_classes = {
                'AdminUser': AdminUser,
                'ContentCreatorUser': ContentCreatorUser
            }

            user_class = user_classes.get(user_type, ViewerUser)
            user = user_class(
                user_data['user_id'], user_data['username'],
                user_data['email'], user_data['password_hash'], role
            )

            if 'created_at' in user_data:
                user.created_at = datetime.fromisoformat(user_data['created_at'])
            if 'is_active' in user_data:
                user.is_active = user_data['is_active']

            return user

        except Exception as e:
            print(f"System: Error deserializing user: {e}")
            return None

    def _update_indexes(self, user: BaseUser):
        self.__username_index[user.username.lower()] = user.user_id
        self.__email_index[user.email.lower()] = user.user_id

    def create_user(self, user: BaseUser) -> BaseUser:
        print(f"System: Creating user {user.user_id} with username '{user.username}'")

        if not isinstance(user, BaseUser):
            raise TypeError("User must be instance of BaseUser")

        if not self._validate_user_data(user):
            raise ValueError("User validation failed")

        if user.user_id in self.__users:
            raise DuplicateUserException(f"User with ID {user.user_id} already exists")

        if user.username.lower() in self.__username_index:
            raise DuplicateUserException(f"Username '{user.username}' already exists")

        if user.email.lower() in self.__email_index:
            raise DuplicateUserException(f"Email '{user.email}' already exists")

        self.__users[user.user_id] = user
        self._update_indexes(user)
        self.__last_modified = datetime.now()

        try:
            self._save_to_file()
            print(f"System: User {user.user_id} created and saved successfully")
        except Exception as e:
            del self.__users[user.user_id]
            print(f"System: Error saving user, rolled back: {e}")
            raise

        return user

    def get_user_by_id(self, user_id: str) -> BaseUser:
        # ID ile kullanıcı getir
        if not isinstance(user_id, str) or not user_id.strip():
            raise ValueError("User ID must be non-empty string")

        user_id = user_id.strip()
        if user_id not in self.__users:
            raise UserNotFoundException(f"User with ID {user_id} not found")

        return self.__users[user_id]

    def get_user_by_username(self, username: str) -> BaseUser:
        # Username ile kullanıcı getir
        if not isinstance(username, str) or not username.strip():
            raise ValueError("Username must be non-empty string")

        username_lower = username.strip().lower()
        if username_lower not in self.__username_index:
            raise UserNotFoundException(f"User with username '{username}' not found")

        return self.__users[self.__username_index[username_lower]]

    def get_all_users(self) -> List[BaseUser]:
        return list(self.__users.values())

    def get_users_by_role(self, role: UserRole) -> List[BaseUser]:
        return [user for user in self.__users.values() if user.role == role]

    def get_user_count(self) -> int:
        return len(self.__users)

    def _validate_user_data(self, user: BaseUser) -> bool:
        # Kullanıcı verilerini doğrula
        if not user.user_id or len(user.user_id.strip()) < 3:
            return False

        if not user.username or len(user.username.strip()) < 3:
            return False

        if not user.email or '@' not in user.email:
            return False

        if not user.password or len(user.password) < 8:
            return False

        return True

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

# --------------------------------------- 7. gun

    def _deserialize_channel(self, channel_data: Dict[str, Any]) -> Optional[BaseChannel]:
        # Dictionary'den kanal oluştur
        try:
            channel_class = channel_data.get('channel_class', 'PublicChannel')
            channel_type = ChannelType(channel_data['channel_type'])

            channel_classes = {
                'PublicChannel': PublicChannel,
                'PrivateChannel': PrivateChannel
            }

            channel_cls = channel_classes.get(channel_class, PremiumChannel)
            channel = channel_cls(
                channel_data['channel_id'], channel_data['name'],
                channel_data['description'], channel_data['owner_id'], channel_type
            )

            # Ek alanları ayarla
            if 'status' in channel_data:
                channel.status = ChannelStatus(channel_data['status'])
            if 'created_at' in channel_data:
                channel.created_at = datetime.fromisoformat(channel_data['created_at'])
            if 'subscriber_count' in channel_data:
                channel.subscriber_count = channel_data['subscriber_count']
            if 'moderators' in channel_data:
                channel.moderators = set(channel_data['moderators'])

            return channel

        except Exception as e:
            print(f"System: Error deserializing channel: {e}")
            return None

    def _update_indexes(self, channel: BaseChannel):
        # İndeksleri güncelle
        if channel.owner_id not in self.__owner_index:
            self.__owner_index[channel.owner_id] = []
        if channel.channel_id not in self.__owner_index[channel.owner_id]:
            self.__owner_index[channel.owner_id].append(channel.channel_id)

        if channel.channel_type not in self.__type_index:
            self.__type_index[channel.channel_type] = []
        if channel.channel_id not in self.__type_index[channel.channel_type]:
            self.__type_index[channel.channel_type].append(channel.channel_id)

    def create_channel(self, channel: BaseChannel) -> BaseChannel:
        # Yeni kanal oluştur
        print(f"System: Creating channel {channel.channel_id} with name '{channel.name}'")

        if not isinstance(channel, BaseChannel):
            raise TypeError("Channel must be instance of BaseChannel")

        if not self._validate_channel_data(channel):
            raise ValueError("Channel validation failed")

        # Duplicate kontrolü
        if channel.channel_id in self.__channels:
            raise DuplicateChannelException(f"Channel with ID {channel.channel_id} already exists")

        # Kanalı ekle
        self.__channels[channel.channel_id] = channel
        self._update_indexes(channel)
        self.__last_modified = datetime.now()

        try:
            self._save_to_file()
            print(f"System: Channel {channel.channel_id} created and saved successfully")
        except Exception as e:
            del self.__channels[channel.channel_id]
            print(f"System: Error saving channel, rolled back: {e}")
            raise

        return channel

    def get_channel_by_id(self, channel_id: str) -> BaseChannel:
        # ID ile kanal getir
        if not isinstance(channel_id, str) or not channel_id.strip():
            raise ValueError("Channel ID must be non-empty string")

        channel_id = channel_id.strip()
        if channel_id not in self.__channels:
            raise ChannelNotFoundException(f"Channel with ID {channel_id} not found")

        return self.__channels[channel_id]

    def get_all_channels(self) -> List[BaseChannel]:
        return list(self.__channels.values())

    def get_channels_by_owner(self, owner_id: str) -> List[BaseChannel]:
        if owner_id not in self.__owner_index:
            return []

        channel_ids = self.__owner_index[owner_id]
        return [self.__channels[cid] for cid in channel_ids if cid in self.__channels]

    def get_channels_by_type(self, channel_type: ChannelType) -> List[BaseChannel]:
        if channel_type not in self.__type_index:
            return []

        channel_ids = self.__type_index[channel_type]
        return [self.__channels[cid] for cid in channel_ids if cid in self.__channels]

    def get_channel_count(self) -> int:
        return len(self.__channels)

    def _validate_channel_data(self, channel: BaseChannel) -> bool:
        # Kanal verilerini doğrula
        return (channel.channel_id and len(channel.channel_id.strip()) >= 3 and
                channel.name and len(channel.name.strip()) >= 3 and
                channel.description and len(channel.description.strip()) >= 10 and
                channel.owner_id and len(channel.owner_id.strip()) >= 3)

    @staticmethod
    def validate_channel_name(name: str) -> bool:
        return (isinstance(name, str) and name.strip() and 3 <= len(name.strip()) <= 50)

    @staticmethod
    def validate_channel_description(description: str) -> bool:
        return (isinstance(description, str) and description.strip() and
                10 <= len(description.strip()) <= 500)
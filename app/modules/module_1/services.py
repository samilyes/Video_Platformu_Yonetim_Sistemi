from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from .base import (
    BaseUser,
    BaseChannel,
    UserRole,
    ChannelStatus,
    ChannelType,
    UserNotFoundException,
    ChannelNotFoundException,
    # DuplicateUserException, DuplicateChannelException
)
from .implementations import PersonalChannel, BrandChannel, KidsChannel
from .repository import UserRepository, ChannelRepository


@dataclass(frozen=True)
class ServiceResult:
    ok: bool
    message: str = ""
    data: Optional[Dict[str, Any]] = None


class UserService:
    # Kullanıcı ile ilgili

    def __init__(self, user_repo: Optional[UserRepository] = None):
        self._user_repo = user_repo or UserRepository()

    @property
    def repo(self) -> UserRepository:
        return self._user_repo

    def create_user(self, user: BaseUser) -> BaseUser:
        # Repository zaten validasyon + duplicate kontrol yapıyor.
        return self._user_repo.create_user(user)

    def get_user(self, user_id: str) -> BaseUser:
        return self._user_repo.get_user_by_id(user_id)

    def find_by_username(self, username: str) -> BaseUser:
        return self._user_repo.get_user_by_username(username)

    def list_users(self, role: Optional[UserRole] = None) -> List[BaseUser]:
        if role is None:
            return self._user_repo.get_all_users()
        return self._user_repo.get_users_by_role(role)

    def deactivate_user(self, user_id: str) -> ServiceResult:
        try:
            self._user_repo.set_user_active(user_id, False)
            return ServiceResult(ok=True, message="User deactivated", data={"user_id": user_id})
        except UserNotFoundException as e:
            return ServiceResult(ok=False, message=str(e))


class ChannelService:
    # Kanal ile ilgili , yetki kuralları

    def __init__(
        self,
        channel_repo: Optional[ChannelRepository] = None,
        user_repo: Optional[UserRepository] = None,
    ):
        self._channel_repo = channel_repo or ChannelRepository()
        self._user_repo = user_repo or UserRepository()

    @property
    def channels(self) -> ChannelRepository:
        return self._channel_repo

    @property
    def users(self) -> UserRepository:
        return self._user_repo

    def create_channel(self, channel: BaseChannel, requested_by_user_id: Optional[str] = None) -> BaseChannel:

        #Kanal oluşturma use-case.
        # owner user var mı kontrol eder
        # istenirse requested_by_user_id ile basit yetki kontrolü yapılır

        # Owner mevcut mu?
        self._user_repo.get_user_by_id(channel.owner_id)

        # requested_by verilmişse ve owner değilse sadece admin oluşturabilsin
        if requested_by_user_id and requested_by_user_id != channel.owner_id:
            requester = self._user_repo.get_user_by_id(requested_by_user_id)
            if requester.role != UserRole.ADMIN:
                raise PermissionError("Only ADMIN can create channel on behalf of another user")

        return self._channel_repo.create_channel(channel)

    def create_channel_by_type(
        self,
        channel_type: ChannelType,
        channel_id: str,
        name: str,
        description: str,
        owner_id: str,
        requested_by_user_id: Optional[str] = None,
    ) -> BaseChannel:
        # ChannelType'a göre doğru sınıfı seçip kanal oluşturur

        if channel_type == ChannelType.PERSONAL:
            channel = PersonalChannel(channel_id, name, description, owner_id)
        elif channel_type == ChannelType.BRAND:
            channel = BrandChannel(channel_id, name, description, owner_id)
        elif channel_type == ChannelType.KIDS:
            channel = KidsChannel(channel_id, name, description, owner_id)
        else:
            raise ValueError(f"Unsupported channel_type for factory create: {channel_type}")

        return self.create_channel(channel, requested_by_user_id=requested_by_user_id)

    def get_channel(self, channel_id: str) -> BaseChannel:
        return self._channel_repo.get_channel_by_id(channel_id)

    def list_channels(
        self,
        owner_id: Optional[str] = None,
        channel_type: Optional[ChannelType] = None,
        category: Optional[str] = None,
    ) -> List[BaseChannel]:
        if owner_id is not None:
            return self._channel_repo.get_channels_by_owner(owner_id)
        if channel_type is not None:
            return self._channel_repo.get_channels_by_type(channel_type)
        if category is not None:
            return self._channel_repo.get_channel_by_category(category)
        return self._channel_repo.get_all_channels()

    def change_status(self, channel_id: str, new_status: ChannelStatus, requested_by_user_id: str) -> ServiceResult:
        # Kanal durum değişimi.
        # owner veya ADMIN değiştirebilir

        try:
            channel = self._channel_repo.get_channel_by_id(channel_id)
            requester = self._user_repo.get_user_by_id(requested_by_user_id)

            if requested_by_user_id != channel.owner_id and requester.role != UserRole.ADMIN:
                return ServiceResult(ok=False, message="Not authorized")

            self._channel_repo.set_channel_status(channel_id, new_status)
            return ServiceResult(ok=True, message="Status updated", data={"channel_id": channel_id, "status": new_status.value})

        except (ChannelNotFoundException, UserNotFoundException) as e:
            return ServiceResult(ok=False, message=str(e))

    def can_access(self, channel_id: str, user_id: str) -> bool:
        #Kanal erişim kontrolü BaseChannel.can_user_access

        channel = self._channel_repo.get_channel_by_id(channel_id)
        user = self._user_repo.get_user_by_id(user_id)
        return channel.can_user_access(user_id, user.role)

    def get_statistics(self, channel_id: str, video_repo: Any = None) -> Dict[str, Any]:
        # Kanal istatistiklerini döndürür.

        channel = self._channel_repo.get_channel_by_id(channel_id)

        # implementations.py tarafı bazı sınıflarda repo parametresi
        try:
            return channel.get_channel_statistics(repo=video_repo)
        except TypeError:
            return channel.get_channel_statistics()


class Module1ServiceFacade:
    # Module-1 servislerine tek giriş noktası

    def __init__(
        self,
        user_repo: Optional[UserRepository] = None,
        channel_repo: Optional[ChannelRepository] = None,
    ):
        self.users = UserService(user_repo=user_repo)
        # aynı user_repo instance'ını paylaşmak için:
        self.channels = ChannelService(channel_repo=channel_repo, user_repo=self.users.repo)

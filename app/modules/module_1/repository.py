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
"""
Video Modülü
============
Bu paket, Akıllı Video Platformu için Video ve İçerik Yönetim Modülünü içerir.
Video oluşturma, depolama, yaşam döngüsü yönetimi ve erişim işlemlerini yönetir.
"""

import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from app.modules.module_2.base import VideoBase, VideoStatus, VideoVisibility, VideoError, VideoNotFoundError
    from app.modules.module_2.implementations import StandardVideo, LiveStreamVideo, ShortVideo
    from app.modules.module_2.services import VideoService
    from app.modules.module_2.repository import VideoRepository
except ImportError:
    from .base import VideoBase, VideoStatus, VideoVisibility, VideoError, VideoNotFoundError
    from .implementations import StandardVideo, LiveStreamVideo, ShortVideo
    from .services import VideoService
    from .repository import VideoRepository

__all__ = [
    'VideoBase',
    'VideoStatus',
    'VideoVisibility',
    'StandardVideo',
    'LiveStreamVideo',
    'ShortVideo',
    'VideoRepository',
    'VideoService',
    'VideoError',
    'VideoNotFoundError',
]
"""
Initialize platforms package
"""

from .facebook_handler import FacebookHandler
from .instagram_handler import InstagramHandler
from .google_ads_handler import GoogleAdsHandler

__all__ = [
    'FacebookHandler',
    'InstagramHandler',
    'GoogleAdsHandler'
]

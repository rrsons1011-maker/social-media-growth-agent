"""
Instagram Platform Handler
Manages all Instagram-related operations including posting, stories, reels, and engagement.
"""

import logging
import requests
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class InstagramHandler:
    """Handler for Instagram platform operations."""

    def __init__(self, access_token: str, business_account_id: str):
        """
        Initialize Instagram handler.

        Args:
            access_token (str): Instagram Graph API access token
            business_account_id (str): Instagram business account ID
        """
        self.access_token = access_token
        self.business_account_id = business_account_id
        self.graph_url = "https://graph.instagram.com/v18.0"

    def post(self, content: str, media_url: Optional[str] = None, post_type: str = 'feed') -> Dict:
        """
        Post content to Instagram.

        Args:
            content (str): Caption text
            media_url (str): URL to image/video
            post_type (str): Type of post (feed, story, reel)

        Returns:
            Dict: Response with post ID and status
        """
        try:
            if post_type == 'feed':
                return self._post_feed(content, media_url)
            elif post_type == 'story':
                return self._post_story(content, media_url)
            elif post_type == 'reel':
                return self._post_reel(content, media_url)
            else:
                raise ValueError(f"Unknown post type: {post_type}")
        except Exception as e:
            logger.error(f"Failed to post on Instagram: {str(e)}")
            return {'success': False, 'error': str(e)}

    def _post_feed(self, caption: str, media_url: str) -> Dict:
        """Post to Instagram feed."""
        try:
            # Create container
            container_endpoint = f"{self.graph_url}/{self.business_account_id}/media"
            container_params = {
                'image_url': media_url,
                'caption': caption,
                'access_token': self.access_token
            }

            container_response = requests.post(container_endpoint, data=container_params)
            container_response.raise_for_status()
            container_id = container_response.json().get('id')

            # Publish
            publish_endpoint = f"{self.graph_url}/{self.business_account_id}/media_publish"
            publish_params = {
                'creation_id': container_id,
                'access_token': self.access_token
            }

            publish_response = requests.post(publish_endpoint, data=publish_params)
            publish_response.raise_for_status()

            result = publish_response.json()
            logger.info(f"Feed post created on Instagram: {result.get('id')}")
            return {
                'success': True,
                'post_id': result.get('id'),
                'message': 'Feed post published successfully'
            }
        except Exception as e:
            logger.error(f"Failed to post feed on Instagram: {str(e)}")
            return {'success': False, 'error': str(e)}

    def _post_story(self, caption: str, media_url: str) -> Dict:
        """Post to Instagram story."""
        try:
            endpoint = f"{self.graph_url}/{self.business_account_id}/stories"
            params = {
                'image_url': media_url,
                'caption': caption,
                'access_token': self.access_token
            }

            response = requests.post(endpoint, data=params)
            response.raise_for_status()

            result = response.json()
            logger.info(f"Story created on Instagram: {result.get('id')}")
            return {
                'success': True,
                'story_id': result.get('id'),
                'message': 'Story published successfully'
            }
        except Exception as e:
            logger.error(f"Failed to post story on Instagram: {str(e)}")
            return {'success': False, 'error': str(e)}

    def _post_reel(self, caption: str, video_url: str) -> Dict:
        """Post to Instagram reels."""
        try:
            # Similar to feed but optimized for video
            endpoint = f"{self.graph_url}/{self.business_account_id}/media"
            params = {
                'video_url': video_url,
                'caption': caption,
                'media_type': 'REELS',
                'access_token': self.access_token
            }

            response = requests.post(endpoint, data=params)
            response.raise_for_status()

            result = response.json()
            logger.info(f"Reel created on Instagram: {result.get('id')}")
            return {
                'success': True,
                'reel_id': result.get('id'),
                'message': 'Reel published successfully'
            }
        except Exception as e:
            logger.error(f"Failed to post reel on Instagram: {str(e)}")
            return {'success': False, 'error': str(e)}

    def get_analytics(self, date_range: Dict) -> Dict:
        """
        Get analytics for Instagram business account.

        Args:
            date_range (Dict): Date range with 'start' and 'end'

        Returns:
            Dict: Analytics data
        """
        try:
            endpoint = f"{self.graph_url}/{self.business_account_id}/insights"
            params = {
                'metric': 'impressions,reach,profile_views,follower_count',
                'period': 'day',
                'access_token': self.access_token,
                'date_start': date_range.get('start'),
                'date_end': date_range.get('end')
            }

            response = requests.get(endpoint, params=params)
            response.raise_for_status()

            logger.info("Analytics retrieved from Instagram")
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get Instagram analytics: {str(e)}")
            return {}

    def get_recent_posts(self, limit: int = 10) -> List[Dict]:
        """
        Get recent posts from Instagram account.

        Args:
            limit (int): Number of posts to retrieve

        Returns:
            List[Dict]: List of posts
        """
        try:
            endpoint = f"{self.graph_url}/{self.business_account_id}/media"
            params = {
                'fields': 'id,caption,media_type,timestamp,like_count,comments_count',
                'limit': limit,
                'access_token': self.access_token
            }

            response = requests.get(endpoint, params=params)
            response.raise_for_status()

            logger.info(f"Retrieved {limit} posts from Instagram")
            return response.json().get('data', [])
        except Exception as e:
            logger.error(f"Failed to get Instagram posts: {str(e)}")
            return []

    def auto_engage(self) -> int:
        """
        Automatically engage with audience on Instagram.

        Returns:
            int: Number of engagements made
        """
        engagement_count = 0
        try:
            # Get recent posts
            posts = self.get_recent_posts()

            for post in posts:
                post_id = post.get('id')
                
                # Like the post (if not already liked)
                like_endpoint = f"{self.graph_url}/{post_id}/likes"
                like_params = {'access_token': self.access_token}
                
                try:
                    requests.post(like_endpoint, data=like_params)
                    engagement_count += 1
                except:
                    pass

                # Get and respond to comments
                comments_endpoint = f"{self.graph_url}/{post_id}/comments"
                comments_response = requests.get(
                    comments_endpoint,
                    params={'access_token': self.access_token}
                )

                if comments_response.status_code == 200:
                    comments = comments_response.json().get('data', [])
                    for comment in comments[:3]:  # Limit to 3 comments
                        self._like_comment(comment.get('id'))
                        engagement_count += 1

            logger.info(f"Instagram engagement complete: {engagement_count} actions")
            return engagement_count
        except Exception as e:
            logger.error(f"Failed to engage on Instagram: {str(e)}")
            return engagement_count

    def _like_comment(self, comment_id: str) -> bool:
        """Like a specific comment."""
        try:
            endpoint = f"{self.graph_url}/{comment_id}/likes"
            params = {'access_token': self.access_token}
            response = requests.post(endpoint, data=params)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to like comment: {str(e)}")
            return False

    def get_account_info(self) -> Dict:
        """Get business account information."""
        try:
            endpoint = f"{self.graph_url}/{self.business_account_id}"
            params = {
                'fields': 'id,username,name,followers_count,follows_count,biography',
                'access_token': self.access_token
            }
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get account info: {str(e)}")
            return {}

import os
import logging
from typing import List, Dict, Any
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from config.config import get_config

class SlackIntegration:
    """Slack integration for fetching feature requests"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        
        # Initialize Slack client
        if self.config.slack.bot_token:
            self.client = WebClient(token=self.config.slack.bot_token)
        else:
            self.client = None
            self.logger.warning("Slack bot token not configured")
    
    def get_channel_messages(self, channel_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch feature requests from a Slack channel"""
        if not self.client:
            self.logger.error("Slack client not initialized")
            return []
        
        try:
            # First, get channel ID from name
            channel_id = self._get_channel_id(channel_name)
            if not channel_id:
                self.logger.error(f"Channel '{channel_name}' not found")
                return []
            
            # Try to fetch messages from channel
            try:
                response = self.client.conversations_history(
                    channel=channel_id,
                    limit=limit
                )
                
                if response['ok']:
                    feature_requests = []
                    for message in response['messages']:
                        if 'user' in message and 'text' in message:
                            feature_requests.append({
                                'user': message['user'],
                                'text': message['text'],
                                'timestamp': message.get('ts'),
                                'type': 'feature_request'
                            })
                    
                    return feature_requests
                else:
                    self.logger.error(f"Slack API error: {response['error']}")
                    return []
                        
            except SlackApiError as e:
                self.logger.error(f"Slack API error: {e}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error fetching Slack messages: {e}")
            return []
    
    def _get_channel_id(self, channel_name: str) -> str:
        """Get channel ID from channel name"""
        try:
            response = self.client.conversations_list()
            for channel in response['channels']:
                if channel['name'] == channel_name:
                    return channel['id']
            return ""
        except SlackApiError as e:
            self.logger.error(f"Error getting channel list: {e}")
            return ""
    
    def send_message(self, channel: str, message: str) -> bool:
        """Send a message to a Slack channel"""
        if not self.client:
            self.logger.error("Slack client not initialized")
            return False
        
        try:
            channel_id = self._get_channel_id(channel)
            if not channel_id:
                self.logger.error(f"Channel '{channel}' not found")
                return False
            
            response = self.client.chat_postMessage(
                channel=channel_id,
                text=message
            )
            return response['ok']
            
        except SlackApiError as e:
            self.logger.error(f"Error sending Slack message: {e}")
            return False
    
    def get_feedback_messages(self, feedback_channel: str = "customer-feedbacks") -> List[Dict[str, Any]]:
        """Get feedback messages from the designated feedback channel"""
        return self.get_channel_messages(feedback_channel, limit=50)

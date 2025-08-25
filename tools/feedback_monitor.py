from typing import List, Dict, Any
import logging
import requests
from datetime import datetime
from config.config import get_config
from integrations.slack_integration import SlackIntegration

class FeedbackMonitor:
    """Tool to monitor and aggregate feedback from multiple sources"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        self.slack_integration = SlackIntegration()
    
    def gather_feedback(self) -> List[Dict[str, Any]]:
        """Gather feedback from all available sources"""
        self.logger.info("Gathering feedback from all sources...")
        
        feedback_items = []
        
        # Gather feedback from Slack
        slack_feedback = self.gather_slack_feedback()
        feedback_items.extend(slack_feedback)
        
        # Gather feedback from web sources
        web_feedback = self.gather_web_feedback()
        feedback_items.extend(web_feedback)
        
        # Gather feedback from social media (simulated)
        social_media_feedback = self.gather_social_media_feedback()
        feedback_items.extend(social_media_feedback)
        
        # Gather feedback from email (simulated)
        email_feedback = self.gather_email_feedback()
        feedback_items.extend(email_feedback)
        
        self.logger.info(f"Gathered {len(feedback_items)} feedback items total")
        return feedback_items
    
    def gather_slack_feedback(self, channel_name: str = "feedback-and-issues") -> List[Dict[str, Any]]:
        """Gather feedback from Slack channel"""
        self.logger.info(f"Gathering feedback from Slack channel: {channel_name}")
        
        messages = self.slack_integration.get_channel_messages(channel_name)
        
        feedback_items = []
        for message in messages:
            feedback_item = {
                'source': 'slack',
                'channel': channel_name,
                'user': message.get('user', 'unknown'),
                'text': message.get('text', ''),
                'timestamp': message.get('timestamp'),
                'raw_message': message
            }
            feedback_items.append(feedback_item)
        
        self.logger.info(f"Found {len(feedback_items)} feedback messages in Slack")
        return feedback_items
    
    def gather_web_feedback(self) -> List[Dict[str, Any]]:
        """Gather feedback from web sources (simulated for now)"""
        self.logger.info("Gathering feedback from web sources...")
        
        # Simulated web feedback - in a real implementation, this would scrape
        # forums, review sites, or use web APIs
        web_feedback = [
            {
                'source': 'web_forum',
                'user': 'forum_user_123',
                'text': 'The new analytics dashboard is great but needs more export options',
                'timestamp': datetime.now().isoformat(),
                'url': 'https://example.com/forum/thread/123'
            },
            {
                'source': 'review_site',
                'user': 'reviewer_456',
                'text': 'Love the product! Would be perfect with better mobile support',
                'timestamp': datetime.now().isoformat(),
                'rating': 4.5
            }
        ]
        
        self.logger.info(f"Found {len(web_feedback)} feedback items from web sources")
        return web_feedback
    
    def gather_social_media_feedback(self) -> List[Dict[str, Any]]:
        """Gather feedback from social media platforms (simulated)"""
        self.logger.info("Gathering feedback from social media...")
        
        # Simulated social media feedback
        social_feedback = [
            {
                'source': 'twitter',
                'user': '@tech_enthusiast',
                'text': 'Just tried the new feature - amazing work team! #innovation',
                'timestamp': datetime.now().isoformat(),
                'likes': 23,
                'retweets': 5
            },
            {
                'source': 'linkedin',
                'user': 'Industry Professional',
                'text': 'Impressive update to the platform. The UI improvements are particularly noteworthy.',
                'timestamp': datetime.now().isoformat(),
                'reactions': 15
            }
        ]
        
        self.logger.info(f"Found {len(social_feedback)} feedback items from social media")
        return social_feedback
    
    def gather_email_feedback(self) -> List[Dict[str, Any]]:
        """Gather feedback from email (simulated)"""
        self.logger.info("Gathering feedback from email...")
        
        # Simulated email feedback
        email_feedback = [
            {
                'source': 'email',
                'user': 'customer@example.com',
                'text': 'The support team was very helpful in resolving my issue quickly.',
                'timestamp': datetime.now().isoformat(),
                'subject': 'Great support experience'
            },
            {
                'source': 'email',
                'user': 'user@company.com',
                'text': 'We need better integration with our existing CRM system.',
                'timestamp': datetime.now().isoformat(),
                'subject': 'Feature request: CRM integration'
            }
        ]
        
        self.logger.info(f"Found {len(email_feedback)} feedback items from email")
        return email_feedback
    
    def analyze_sentiment(self, feedback_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform sentiment analysis on feedback items using TextBlob"""
        self.logger.info("Analyzing sentiment of feedback items using TextBlob...")
        
        try:
            from textblob import TextBlob
        except ImportError:
            self.logger.warning("TextBlob not available, falling back to simple sentiment analysis")
            return self._simple_sentiment_analysis(feedback_items)
        
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        sentiment_scores = []
        
        for item in feedback_items:
            text = item.get('text', '')
            if not text:
                item['sentiment'] = 'neutral'
                sentiment_counts['neutral'] += 1
                item['sentiment_score'] = 0.0
                continue
                
            # Analyze sentiment using TextBlob
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            item['sentiment_score'] = polarity
            
            # Classify sentiment based on polarity score
            if polarity > 0.1:
                sentiment = "positive"
            elif polarity < -0.1:
                sentiment = "negative"
            else:
                sentiment = "neutral"
                
            item['sentiment'] = sentiment
            sentiment_counts[sentiment] += 1
            sentiment_scores.append(polarity)
        
        # Calculate average sentiment score
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        
        return {
            "total_feedback": len(feedback_items),
            "sentiment_distribution": sentiment_counts,
            "overall_sentiment": self._calculate_overall_sentiment(sentiment_counts),
            "average_sentiment_score": round(avg_sentiment, 3),
            "feedback_items": feedback_items
        }
    
    def _simple_sentiment_analysis(self, feedback_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fallback simple sentiment analysis"""
        self.logger.info("Using simple sentiment analysis...")
        
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        
        for item in feedback_items:
            text = item.get('text', '').lower()
            sentiment = self._classify_sentiment_simple(text)
            item['sentiment'] = sentiment
            sentiment_counts[sentiment] += 1
            item['sentiment_score'] = 1.0 if sentiment == 'positive' else -1.0 if sentiment == 'negative' else 0.0
        
        return {
            "total_feedback": len(feedback_items),
            "sentiment_distribution": sentiment_counts,
            "overall_sentiment": self._calculate_overall_sentiment(sentiment_counts),
            "average_sentiment_score": 0.0,  # Not calculated in simple mode
            "feedback_items": feedback_items
        }
    
    def _classify_sentiment_simple(self, text: str) -> str:
        """Simple sentiment classification based on keywords"""
        positive_words = ['great', 'awesome', 'love', 'amazing', 'excellent', 'good', 'perfect', 'wonderful', 'impressive', 'fantastic']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'disappointing', 'poor', 'crash', 'bug', 'issue', 'problem', 'frustrating', 'broken']
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _calculate_overall_sentiment(self, sentiment_counts: Dict[str, int]) -> str:
        """Calculate overall sentiment from distribution"""
        if sentiment_counts["positive"] > sentiment_counts["negative"]:
            return "positive"
        elif sentiment_counts["negative"] > sentiment_counts["positive"]:
            return "negative"
        else:
            return "neutral"
    
    def calculate_impact_score(self, feedback_item: Dict[str, Any]) -> float:
        """Calculate impact score for a feedback item"""
        # Simple impact scoring based on sentiment and text length
        sentiment_weights = {"positive": 0.3, "negative": 0.7, "neutral": 0.1}
        
        sentiment = feedback_item.get('sentiment', 'neutral')
        text_length = len(feedback_item.get('text', ''))
        
        sentiment_score = sentiment_weights.get(sentiment, 0.1)
        length_score = min(text_length / 100, 1.0)  # Normalize text length
        
        return (sentiment_score * 0.7) + (length_score * 0.3)
    
    def get_feature_requests(self, feedback_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract feature requests from feedback"""
        feature_keywords = ['feature', 'request', 'add', 'implement', 'support', 'would like', 'want', 'need']
        
        feature_requests = []
        for item in feedback_items:
            text = item.get('text', '').lower()
            if any(keyword in text for keyword in feature_keywords):
                # Calculate impact score for prioritization
                impact_score = self.calculate_impact_score(item)
                feature_request = item.copy()
                feature_request['impact_score'] = impact_score
                feature_requests.append(feature_request)
        
        # Sort by impact score (highest first)
        feature_requests.sort(key=lambda x: x.get('impact_score', 0), reverse=True)
        
        return feature_requests

import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

load_dotenv()

class SlackConfig(BaseModel):
    """Configuration for Slack integration"""
    bot_token: Optional[str] = Field(default=os.getenv("SLACK_BOT_TOKEN"))
    app_token: Optional[str] = Field(default=os.getenv("SLACK_APP_TOKEN"))
    channel_id: Optional[str] = Field(default=os.getenv("SLACK_CHANNEL_ID"))

class NotionConfig(BaseModel):
    """Configuration for Notion integration"""
    api_key: Optional[str] = Field(default=os.getenv("NOTION_API_KEY"))
    database_id: Optional[str] = Field(default=os.getenv("NOTION_DATABASE_ID"))

class GitHubConfig(BaseModel):
    """Configuration for GitHub integration"""
    token: Optional[str] = Field(default=os.getenv("GITHUB_TOKEN"))
    repo_owner: Optional[str] = Field(default=os.getenv("GITHUB_REPO_OWNER"))
    repo_name: Optional[str] = Field(default=os.getenv("GITHUB_REPO_NAME"))

class GoogleCalendarConfig(BaseModel):
    """Configuration for Google Calendar integration"""
    credentials_path: Optional[str] = Field(default=os.getenv("GOOGLE_CALENDAR_CREDENTIALS_PATH"))
    token_path: Optional[str] = Field(default=os.getenv("GOOGLE_CALENDAR_TOKEN_PATH"))

class LLMConfig(BaseModel):
    """Configuration for LLM providers"""
    provider: str = Field(default="google")
    model: str = Field(default="google/gemini-2.0-flash")
    api_key: Optional[str] = Field(default=os.getenv("GOOGLE_API_KEY"))
    temperature: float = Field(default=0.1)

class AppConfig(BaseModel):
    """Main application configuration"""
    slack: SlackConfig = Field(default_factory=SlackConfig)
    notion: NotionConfig = Field(default_factory=NotionConfig)
    github: GitHubConfig = Field(default_factory=GitHubConfig)
    google_calendar: GoogleCalendarConfig = Field(default_factory=GoogleCalendarConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")

# Global configuration instance
config = AppConfig()

def get_config() -> AppConfig:
    """Get the application configuration"""
    return config

def update_config(new_config: Dict[str, Any]) -> None:
    """Update the configuration with new values"""
    global config
    config = AppConfig(**new_config)

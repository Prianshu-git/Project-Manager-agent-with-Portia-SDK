"""
Notion Integration for PM Agent Workflow
Handles creating and updating PRD documents in Notion
"""

import os
import logging
from typing import Dict, Any, Optional
from notion_client import Client
from notion_client.errors import APIResponseError

logger = logging.getLogger(__name__)

class NotionIntegration:
    """Notion integration for creating and updating PRD documents"""
    
    def __init__(self):
        self.client = None
        self.database_id = None
        self.initialize_notion()
    
    def initialize_notion(self):
        """Initialize Notion client with API key"""
        try:
            # Load environment variables on demand
            from dotenv import load_dotenv
            load_dotenv()
            
            notion_api_key = os.getenv('NOTION_API_KEY')
            database_id = os.getenv('NOTION_DATABASE_ID')
            
            if not notion_api_key or not database_id:
                logger.warning("Notion API key or database ID not configured")
                return
            
            self.client = Client(auth=notion_api_key)
            self.database_id = database_id
            logger.info("✅ Notion client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Notion client: {str(e)}")
    
    def create_prd_page(self, prd_data: Dict[str, Any]) -> Optional[str]:
        """Create a new PRD page in Notion"""
        if not self.client or not self.database_id:
            logger.error("Notion client not initialized")
            return None
        
        try:
            # First, let's check the database schema to understand the available properties
            database = self.client.databases.retrieve(self.database_id)
            logger.info(f"Database properties: {list(database['properties'].keys())}")
            
            # Prepare the page properties based on common Notion database schemas
            properties = {}
            
            # Try different common property names for title
            title_property = self._find_title_property(database)
            if title_property:
                properties[title_property] = {
                    "title": [
                        {
                            "text": {
                                "content": prd_data.get('title', 'Untitled PRD')
                            }
                        }
                    ]
                }
            
            # Try different common property names for status
            status_property = self._find_status_property(database)
            if status_property:
                prop_data = database['properties'][status_property]
                if prop_data['type'] == 'status':
                    # Get available status options
                    status_options = prop_data.get('status', {}).get('options', [])
                    if status_options:
                        # Use the first available status option
                        first_status = status_options[0]['name']
                        properties[status_property] = {
                            "status": {
                                "name": first_status
                            }
                        }
                    else:
                        logger.warning("No status options found, skipping status property")
                elif prop_data['type'] == 'select':
                    # Get available select options
                    select_options = prop_data.get('select', {}).get('options', [])
                    if select_options:
                        # Use the first available select option
                        first_option = select_options[0]['name']
                        properties[status_property] = {
                            "select": {
                                "name": first_option
                            }
                        }
                    else:
                        logger.warning("No select options found, skipping status property")
            
            # Try different common property names for priority
            priority_property = self._find_priority_property(database)
            if priority_property:
                properties[priority_property] = {
                    "select": {
                        "name": prd_data.get('priority', 'Medium')
                    }
                }
            
            # Create the page
            page = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties
            )
            
            logger.info(f"✅ PRD page created in Notion: {page['id']}")
            return page['id']
            
        except APIResponseError as e:
            logger.error(f"Notion API error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error creating Notion page: {str(e)}")
            return None
    
    def _find_title_property(self, database: Dict) -> Optional[str]:
        """Find the title property in the database"""
        for prop_name, prop_data in database['properties'].items():
            if prop_data['type'] == 'title':
                return prop_name
        return "Name"  # Fallback to common default
    
    def _find_status_property(self, database: Dict) -> Optional[str]:
        """Find the status property in the database"""
        for prop_name, prop_data in database['properties'].items():
            if prop_data['type'] == 'select' and 'status' in prop_name.lower():
                return prop_name
            elif prop_data['type'] == 'status':
                return prop_name
        return "Status"  # Fallback to common default
    
    def _find_priority_property(self, database: Dict) -> Optional[str]:
        """Find the priority property in the database"""
        for prop_name, prop_data in database['properties'].items():
            if prop_data['type'] == 'select' and 'priority' in prop_name.lower():
                return prop_name
        return "Priority"  # Fallback to common default
    
    def update_prd_content(self, page_id: str, prd_content: str) -> bool:
        """Update PRD page content with the generated PRD"""
        if not self.client:
            logger.error("Notion client not initialized")
            return False
        
        try:
            # Split PRD content into chunks of 2000 characters or less
            max_length = 2000
            chunks = [prd_content[i:i + max_length] for i in range(0, len(prd_content), max_length)]
            
            # Add PRD content as blocks
            blocks = []
            for chunk in chunks:
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": chunk
                                }
                            }
                        ]
                    }
                })
            
            # Append the content to the page
            self.client.blocks.children.append(
                block_id=page_id,
                children=blocks
            )
            
            logger.info(f"✅ PRD content added to Notion page: {page_id}")
            return True
            
        except APIResponseError as e:
            logger.error(f"Notion API error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error updating Notion page: {str(e)}")
            return False
    
    def create_complete_prd(self, prd_data: Dict[str, Any], prd_content: str) -> Optional[str]:
        """Create a complete PRD with both properties and content"""
        page_id = self.create_prd_page(prd_data)
        if page_id:
            success = self.update_prd_content(page_id, prd_content)
            if success:
                return page_id
        return None

# Global instance
notion_integration = NotionIntegration()

def get_notion_integration() -> NotionIntegration:
    """Get the Notion integration instance"""
    return notion_integration

def create_prd_in_notion(title: str, content: str, priority: str = "Medium") -> Optional[str]:
    """Convenience function to create a PRD in Notion"""
    prd_data = {
        "title": title,
        "priority": priority
    }
    return notion_integration.create_complete_prd(prd_data, content)

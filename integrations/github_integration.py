import os
import logging
from typing import List, Dict, Any, Optional
from github import Github, GithubException
from config.config import get_config

class GitHubIntegration:
    """GitHub integration for creating issues and managing repositories"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        self.client = None
        self.repo = None
        self.initialize_github()
    
    def initialize_github(self):
        """Initialize GitHub client with authentication"""
        try:
            if self.config.github.token:
                self.client = Github(self.config.github.token)
                self.logger.info("GitHub client initialized successfully")
                
                # Get repository
                if self.config.github.repo_owner and self.config.github.repo_name:
                    repo_name = f"{self.config.github.repo_owner}/{self.config.github.repo_name}"
                    self.repo = self.client.get_repo(repo_name)
                    self.logger.info(f"Connected to repository: {repo_name}")
                else:
                    self.logger.warning("GitHub repository not configured")
            else:
                self.logger.warning("GitHub token not configured")
                
        except GithubException as e:
            self.logger.error(f"GitHub initialization failed: {e}")
        except Exception as e:
            self.logger.error(f"Error initializing GitHub: {e}")
    
    def create_issue(self, title: str, body: str, labels: List[str] = None, assignees: List[str] = None) -> Optional[Dict[str, Any]]:
        """Create a GitHub issue"""
        if not self.repo:
            self.logger.error("GitHub repository not initialized")
            return None
        
        try:
            # Create issue
            issue = self.repo.create_issue(
                title=title,
                body=body,
                labels=labels or ["enhancement"],
                assignees=assignees or []
            )
            
            self.logger.info(f"Created GitHub issue: {issue.title} (#{issue.number})")
            
            return {
                "id": issue.id,
                "number": issue.number,
                "title": issue.title,
                "url": issue.html_url,
                "state": issue.state,
                "created_at": issue.created_at.isoformat()
            }
            
        except GithubException as e:
            self.logger.error(f"Failed to create GitHub issue: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error creating GitHub issue: {e}")
            return None
    
    def create_issues_from_features(self, features: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create GitHub issues from feature requests"""
        created_issues = []
        
        for feature in features:
            issue_title = f"Feature: {feature.get('title', 'Unknown Feature')}"
            
            # Build issue body with feature details
            issue_body = self._build_issue_body(feature)
            
            # Determine labels based on priority and type
            labels = self._determine_issue_labels(feature)
            
            # Create the issue
            issue = self.create_issue(issue_title, issue_body, labels)
            
            if issue:
                created_issues.append(issue)
                # Add the issue URL to the feature data
                feature['github_issue_url'] = issue['url']
                feature['github_issue_number'] = issue['number']
        
        return created_issues
    
    def _build_issue_body(self, feature: Dict[str, Any]) -> str:
        """Build a detailed issue body from feature data"""
        body = f"""## Feature Description
{feature.get('description', 'No description provided')}

## Priority: {feature.get('priority', 'Medium')}
**Impact Score:** {feature.get('impact_score', 0)}
**Sentiment:** {feature.get('sentiment', 'neutral')}

## Technical Details
**Estimated Effort:** {feature.get('estimated_effort', 'Not estimated')}
**Business Value:** {feature.get('business_value', 'Not estimated')}
**Target Release:** {feature.get('target_release', 'Not scheduled')}

## Dependencies
{', '.join(feature.get('dependencies', ['None']))}

## Acceptance Criteria
- [ ] Functionality works as described
- [ ] Performance meets requirements
- [ ] UI/UX meets design standards
- [ ] Documentation is complete
- [ ] Testing coverage is adequate

## Additional Context
This feature was automatically generated from user feedback analysis.
"""
        return body
    
    def _determine_issue_labels(self, feature: Dict[str, Any]) -> List[str]:
        """Determine appropriate labels for the issue"""
        labels = ["enhancement", "feature-request"]
        
        # Add priority-based labels
        priority = feature.get('priority', '').lower()
        if priority == 'critical':
            labels.append('priority: critical')
        elif priority == 'high':
            labels.append('priority: high')
        elif priority == 'medium':
            labels.append('priority: medium')
        else:
            labels.append('priority: low')
        
        # Add type-based labels
        title = feature.get('title', '').lower()
        if any(word in title for word in ['ui', 'interface', 'design']):
            labels.append('frontend')
        if any(word in title for word in ['api', 'integration', 'backend']):
            labels.append('backend')
        if any(word in title for word in ['mobile', 'app']):
            labels.append('mobile')
        
        return labels
    
    def update_issue_status(self, issue_number: int, status: str, comment: str = None) -> bool:
        """Update the status of a GitHub issue"""
        if not self.repo:
            self.logger.error("GitHub repository not initialized")
            return False
        
        try:
            issue = self.repo.get_issue(issue_number)
            
            if status.lower() == 'closed':
                issue.edit(state='closed')
                if comment:
                    issue.create_comment(comment)
                self.logger.info(f"Closed issue #{issue_number}")
            elif status.lower() == 'reopened':
                issue.edit(state='open')
                if comment:
                    issue.create_comment(f"Reopened: {comment}")
                self.logger.info(f"Reopened issue #{issue_number}")
            
            return True
            
        except GithubException as e:
            self.logger.error(f"Failed to update issue #{issue_number}: {e}")
            return False
    
    def get_open_issues(self) -> List[Dict[str, Any]]:
        """Get all open issues in the repository"""
        if not self.repo:
            self.logger.error("GitHub repository not initialized")
            return []
        
        try:
            issues = self.repo.get_issues(state='open')
            return [
                {
                    'number': issue.number,
                    'title': issue.title,
                    'url': issue.html_url,
                    'state': issue.state,
                    'created_at': issue.created_at.isoformat(),
                    'labels': [label.name for label in issue.labels]
                }
                for issue in issues
            ]
            
        except GithubException as e:
            self.logger.error(f"Failed to get open issues: {e}")
            return []

#!/usr/bin/env python3
"""
UI for selecting features to continue the PM Agentic AI workflow
Integrates with Portia SDK for actual workflow execution
"""

import os
import sys
import json
import logging
from dotenv import load_dotenv
from pm_agent_workflow import PMAgentWorkflow  # Import the new workflow controller

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FeatureSelectionUI:
    """UI for selecting features and managing workflow continuation"""
    
    def __init__(self):
        self.features = []
        self.selected_feature = None
        self.workflow = PMAgentWorkflow()  # Initialize the workflow controller
    
    def load_features_from_analysis(self, analysis_file='feedback_analysis.json'):
        """Load features from feedback analysis file"""
        try:
            with open(analysis_file, 'r') as f:
                data = json.load(f)
            
            self.features = data.get('feature_requests', [])
            logger.info(f"Loaded {len(self.features)} feature requests from analysis")
            return True
        except FileNotFoundError:
            logger.error(f"Analysis file {analysis_file} not found")
            return False
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in {analysis_file}")
            return False
    
    def display_features(self):
        """Display available features for selection"""
        if not self.features:
            logger.warning("No features available for selection")
            return
        
        logger.info("\n" + "="*60)
        logger.info("FEATURE SELECTION - PM AGENTIC AI WORKFLOW")
        logger.info("="*60)
        
        for i, feature in enumerate(self.features):
            title = self._extract_feature_title(feature.get('text', ''))
            impact_score = feature.get('impact_score', 0)
            logger.info(f"{i + 1}. {title} (Impact Score: {impact_score:.2f})")
            logger.info(f"   Source: {feature.get('source', 'Unknown')}")
            logger.info(f"   User: {feature.get('user', 'Unknown')}")
            logger.info("")
    
    def _extract_feature_title(self, text):
        """Extract meaningful title from feature text"""
        if "Slack integration" in text or "Slack Notifications" in text:
            return "Real-time Slack Notifications"
        elif "Excel plugin" in text or "Excel integration" in text:
            return "Native Excel Integration"
        elif "processing limits" in text or "batch" in text:
            return "Increased Processing Limits"
        else:
            # Extract first line or meaningful snippet
            lines = text.split('\n')
            for line in lines:
                if line.strip() and not line.startswith('>'):
                    return line.strip()[:50] + "..." if len(line) > 50 else line.strip()
            return "New Feature Request"
    
    def select_feature(self):
        """Prompt user to select a feature to continue the workflow"""
        if not self.features:
            logger.error("No features available for selection")
            return None
        
        self.display_features()
        
        try:
            choice = input("\nSelect a feature number to continue (1-{}), or 'q' to quit: ".format(len(self.features)))
            
            if choice.lower() == 'q':
                logger.info("Exiting feature selection.")
                return None
            
            feature_index = int(choice) - 1
            if 0 <= feature_index < len(self.features):
                self.selected_feature = self.features[feature_index]
                title = self._extract_feature_title(self.selected_feature.get('text', ''))
                logger.info(f"✅ Selected: {title}")
                return self.selected_feature
            else:
                logger.error("Invalid selection. Please try again.")
                return self.select_feature()
                
        except ValueError:
            logger.error("Invalid input. Please enter a number.")
            return self.select_feature()
    
    def continue_workflow_with_portia(self, selected_feature):
        """Continue workflow using Portia SDK with the selected feature"""
        title = self._extract_feature_title(selected_feature.get('text', ''))
        logger.info(f"🚀 Continuing workflow with Portia SDK for: {title}")
        
        # Create a prompt for Portia based on the selected feature
        feature_prompt = f"""
        Create a comprehensive product development plan for implementing: {title}
        
        Feature Details:
        {selected_feature.get('text', '')}
        
        Impact Score: {selected_feature.get('impact_score', 0)}
        Source: {selected_feature.get('source', '')}
        User: {selected_feature.get('user', '')}
        
        Please generate a detailed plan including:
        1. Research and analysis
        2. PRD generation
        3. GitHub issue creation
        4. Stakeholder notifications
        5. Timeline and milestones
        """
        
        # Use the workflow controller to generate and execute the plan
        self.workflow.run_workflow(feature_prompt)
        
        return {
            'title': title,
            'description': selected_feature.get('text', ''),
            'impact_score': selected_feature.get('impact_score', 0),
            'source': selected_feature.get('source', ''),
            'user': selected_feature.get('user', '')
        }

def main():
    """Main function to run the feature selection UI"""
    logger.info("Starting PM Agentic AI Feature Selection UI...")
    load_dotenv()
    
    ui = FeatureSelectionUI()
    
    # Load features from analysis
    if not ui.load_features_from_analysis():
        logger.error("Failed to load features. Exiting.")
        return
    
    # Select feature
    selected_feature = ui.select_feature()
    if selected_feature:
        # Continue workflow with Portia SDK
        ui.continue_workflow_with_portia(selected_feature)
    else:
        logger.info("No feature selected. Workflow terminated.")

if __name__ == "__main__":
    main()

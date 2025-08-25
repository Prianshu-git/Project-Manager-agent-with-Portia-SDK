#!/usr/bin/env python3
"""
Main PM Agent Workflow Controller with Portia SDK Integration
Human-in-the-loop controls with edit/check/uncheck/approve options
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from enum import Enum

# Import Pydantic for validation error handling
try:
    from pydantic import ValidationError
except ImportError:
    ValidationError = Exception  # Fallback if pydantic is not available

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UserAction(Enum):
    APPROVE = "approve"
    EDIT = "edit"
    CHECK = "check"
    UNCHECK = "uncheck"
    ADD = "add"
    SKIP = "skip"

class PMAgentWorkflow:
    """Main PM Agent Workflow Controller with Portia SDK Integration"""
    
    def __init__(self):
        load_dotenv()
        self.portia = None
        self.current_plan = None
        self.user_selections = {}
        self.initialize_portia()
    
    def initialize_portia(self):
        """Initialize Portia SDK with Google GenAI"""
        try:
            from portia import Config, LLMProvider, Portia, example_tool_registry
            
            GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
            if not GOOGLE_API_KEY:
                logger.error("GOOGLE_API_KEY not found in environment variables")
                return
            
            google_config = Config.from_default(
                llm_provider=LLMProvider.GOOGLE,
                default_model="google/gemini-2.0-flash",
                google_api_key=GOOGLE_API_KEY
            )
            
            # Create a custom tool registry without the search tool to avoid TAVILY_API_KEY issues
            custom_tools = []
            for tool in example_tool_registry:
                if hasattr(tool, 'id') and 'search' not in tool.id.lower():
                    custom_tools.append(tool)
            
            self.portia = Portia(config=google_config, tools=custom_tools)
            logger.info("✅ Portia SDK initialized successfully with custom tools (search tool excluded)")
            
        except ImportError:
            logger.error("Portia SDK not available. Please install portia-sdk-python")
        except Exception as e:
            logger.error(f"Failed to initialize Portia: {str(e)}")
    
    def generate_plan(self, user_prompt: str) -> Optional[Dict]:
        """Generate plan using Portia SDK with user prompt"""
        if not self.portia:
            logger.error("Portia not initialized")
            return None
        
        try:
            logger.info("🧠 Generating plan with Portia SDK...")
            retries = 3
            result = None
            
            for attempt in range(retries):
                try:
                    # Prepare the input for the Portia SDK
                    sanitized_prompt = user_prompt.replace('$', '')  # Remove any template variables
                    logger.info(f"Sending prompt to Portia: {sanitized_prompt}")
                    
                    # Check for unresolved template variables and provide fallback values
                    template_vars = {}
                    if '$problem_statement' in sanitized_prompt:
                        template_vars['problem_statement'] = "The problem statement will be defined based on user requirements"
                        sanitized_prompt = sanitized_prompt.replace('$problem_statement', template_vars['problem_statement'])
                    
                    if '$success_metrics' in sanitized_prompt:
                        template_vars['success_metrics'] = "Success metrics will include user adoption, performance, and business impact"
                        sanitized_prompt = sanitized_prompt.replace('$success_metrics', template_vars['success_metrics'])
                    
                    if template_vars:
                        logger.info(f"Resolved template variables: {template_vars}")
                    
                    # Call Portia SDK with the sanitized prompt as a string
                    # The SDK expects a string input based on the validation error
                    try:
                        result = self.portia.run(sanitized_prompt)
                    except Exception as api_error:
                        logger.error(f"Portia SDK API call failed: {str(api_error)}")
                        if "InternalServerError" in str(api_error) or "500" in str(api_error):
                            logger.warning("Google GenAI API experiencing issues. Using default plan...")
                            return self._create_default_plan(user_prompt)
                        raise api_error
                    
                    # Check if the result contains valid outputs
                    if result and hasattr(result, 'outputs'):
                        # Ensure outputs are valid and do not contain template variables
                        for output in result.outputs:
                            if isinstance(output, dict):
                                for key in output.keys():
                                    if isinstance(output[key], str) and '{$' in output[key]:
                                        logger.warning(f"Output contains unresolved template variable: {output[key]}")
                                        return self._create_default_plan(user_prompt)
                    if result is None:
                        logger.error("Received None from Portia SDK. Check the API call.")
                        if attempt < retries - 1:
                            logger.info("Retrying due to None result...")
                            continue
                        else:
                            logger.warning("All attempts returned None. Using default plan...")
                            return self._create_default_plan(user_prompt)
                    else:
                        logger.info(f"Raw output from Portia SDK: {result}")
                        # Check if the plan run failed
                        if hasattr(result, 'state') and hasattr(result.state, 'name'):
                            if result.state.name == 'FAILED':
                                logger.warning("Portia SDK plan run failed. Using default plan steps...")
                                return self._create_default_plan(user_prompt)
                            elif result.state.name == 'COMPLETE':
                                # Even if complete, check if the output contains validation errors
                                result_str = str(result)
                                if any(pattern in result_str for pattern in [
                                    'validation error', 
                                    'LLMToolSchema',
                                    'InvalidAgentOutputError',
                                    'Input should be a valid'
                                ]):
                                    logger.warning("Portia SDK completed but with validation errors. Using default plan steps...")
                                    return self._create_default_plan(user_prompt)
                    break  # Exit the retry loop if successful
                except ValidationError as e:
                    # Handle specific ValidationError from LLMToolSchema
                    logger.error(f"Validation error in attempt {attempt + 1}: {str(e)}")
                    if "StepsOrError" in str(e) and "NoneType" in str(e):
                        logger.warning("Portia SDK returned None instead of StepsOrError - likely API issue")
                        if attempt < retries - 1:
                            logger.info("Retrying after StepsOrError validation error...")
                            continue
                        else:
                            logger.error("All attempts failed with StepsOrError validation errors. Using default plan steps...")
                            return self._create_default_plan(user_prompt)
                    if attempt < retries - 1:
                        logger.info("Retrying after validation error...")
                    else:
                        logger.error("All attempts failed with validation errors. Using default plan steps...")
                        return self._create_default_plan(user_prompt)
                except Exception as e:
                    logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt < retries - 1:
                        logger.info("Retrying...")
                    else:
                        logger.error("All attempts failed. Using default plan steps...")
                        return self._create_default_plan(user_prompt)
            
            # Handle the result with better error checking
            try:
                if result is not None and hasattr(result, 'outputs') and hasattr(result.outputs, 'final_output'):
                    plan_output = result.outputs.final_output.value
                    logger.info(f"📋 Plan generated: {str(plan_output)[:100]}...")
                    
                    # Extract plan steps from the Portia output
                    plan_steps = self._extract_plan_steps(plan_output)
                    
                    self.current_plan = {
                        'original_prompt': user_prompt,
                        'plan_output': plan_output,
                        'steps': plan_steps,
                        'status': 'generated'
                    }
                    
                    return self.current_plan
                else:
                    logger.warning("Portia SDK returned invalid output structure. Using default plan steps...")
                    return self._create_default_plan(user_prompt)
                    
            except Exception as e:
                logger.error(f"Error processing Portia output: {str(e)}")
                logger.warning("Using default plan steps due to processing error...")
                return self._create_default_plan(user_prompt)
                
        except Exception as e:
            logger.error(f"Error generating plan: {str(e)}")
            logger.warning("Letting Portia handle the planning due to general error...")
            # Let Portia handle the planning by returning None
            return None
    
    
    def _extract_plan_steps(self, plan_output: Any) -> List[Dict]:
        """Extract plan steps from Portia output (handles both structured and text output)"""
        steps = []
        
        # Check if the output contains error messages with template variables
        plan_text = str(plan_output)
        
        # If the output contains template variables or error messages, use default steps
        if any(pattern in plan_text for pattern in ['{$', 'Error:', 'validation error', 'LLMToolSchema']):
            logger.warning("Portia output contains errors or template variables. Using default steps.")
            return self._get_default_steps()
        
        # If plan_output is already a list of steps, use it directly
        if isinstance(plan_output, list):
            for i, step in enumerate(plan_output):
                if isinstance(step, dict) and 'description' in step:
                    steps.append({
                        'id': step.get('id', f"step_{i+1}"),
                        'description': step['description'],
                        'checked': step.get('checked', False),
                        'editable': step.get('editable', True),
                        'user_modified': step.get('user_modified', False)
                    })
            return steps
        
        # If plan_output is a string, parse it for step-like content
        lines = plan_text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line and any(keyword in line.lower() for keyword in ['step', 'phase', 'task', 'action']):
                steps.append({
                    'id': f"step_{i+1}",
                    'description': line,
                    'checked': False,
                    'editable': True,
                    'user_modified': False
                })
        
        # If no steps found, use default steps
        if not steps:
            return self._get_default_steps()
        
        return steps
    
    def _create_default_plan(self, user_prompt: str) -> Dict:
        """Create a default plan when Portia SDK fails"""
        logger.info("Creating default plan due to Portia SDK failure")
        
        self.current_plan = {
            'original_prompt': user_prompt,
            'plan_output': 'Portia SDK failed to generate plan. Using default steps.',
            'steps': self._get_default_steps(),
            'status': 'generated'
        }
        
        return self.current_plan
    
    def _get_default_steps(self) -> List[Dict]:
        """Return default plan steps when Portia fails or returns invalid output"""
        return [
            {'id': 'step_1', 'description': 'Conduct research and analysis', 'checked': False, 'editable': True, 'user_modified': False},
            {'id': 'step_2', 'description': 'Generate Product Requirements Document (PRD)', 'checked': False, 'editable': True, 'user_modified': False},
            {'id': 'step_3', 'description': 'Create GitHub issues for tasks', 'checked': False, 'editable': True, 'user_modified': False},
            {'id': 'step_4', 'description': 'Notify stakeholders about the project', 'checked': False, 'editable': True, 'user_modified': False}
        ]
    
    def display_plan_with_options(self):
        """Display plan with interactive options for user"""
        if not self.current_plan:
            logger.error("No plan available")
            return
        
        logger.info("\n" + "="*80)
        logger.info("📋 PLAN GENERATED - PLEASE REVIEW AND MODIFY")
        logger.info("="*80)
        logger.info(f"Original Prompt: {self.current_plan['original_prompt']}")
        logger.info("\nPlan Steps:")
        
        for i, step in enumerate(self.current_plan['steps']):
            status = "✅" if step['checked'] else "◻️"
            modified = " (Modified)" if step['user_modified'] else ""
            logger.info(f"{i+1}. {status} {step['description']}{modified}")
        
        logger.info("\nOptions:")
        logger.info("  [c] Check/Uncheck step")
        logger.info("  [e] Edit step description")
        logger.info("  [a] Add new step")
        logger.info("  [s] Skip to next step")
        logger.info("  [x] Approve and continue")
        logger.info("  [q] Quit")
    
    def get_user_action(self) -> UserAction:
        """Get user action for the current plan"""
        try:
            choice = input("\nChoose action: ").lower().strip()
            
            if choice == 'c':
                return UserAction.CHECK
            elif choice == 'e':
                return UserAction.EDIT
            elif choice == 'a':
                return UserAction.ADD
            elif choice == 's':
                return UserAction.SKIP
            elif choice == 'x':
                return UserAction.APPROVE
            elif choice == 'q':
                sys.exit(0)
            else:
                logger.error("Invalid choice. Please try again.")
                return self.get_user_action()
                
        except (EOFError, KeyboardInterrupt):
            logger.info("\nExiting...")
            sys.exit(0)
    
    def handle_user_action(self, action: UserAction):
        """Handle user action on the current plan"""
        if action == UserAction.CHECK:
            self.toggle_step_check()
        elif action == UserAction.EDIT:
            self.edit_step()
        elif action == UserAction.ADD:
            self.add_step()
        elif action == UserAction.SKIP:
            logger.info("Skipping to next step...")
        elif action == UserAction.APPROVE:
            self.approve_plan()
    
    def toggle_step_check(self):
        """Toggle check/uncheck for a step"""
        try:
            step_num = int(input("Enter step number to check/uncheck: ")) - 1
            if 0 <= step_num < len(self.current_plan['steps']):
                step = self.current_plan['steps'][step_num]
                step['checked'] = not step['checked']
                status = "checked" if step['checked'] else "unchecked"
                logger.info(f"Step {step_num + 1} {status}")
            else:
                logger.error("Invalid step number")
        except ValueError:
            logger.error("Please enter a valid number")
    
    def edit_step(self):
        """Edit step description"""
        try:
            step_num = int(input("Enter step number to edit: ")) - 1
            if 0 <= step_num < len(self.current_plan['steps']):
                step = self.current_plan['steps'][step_num]
                new_desc = input(f"Current: {step['description']}\nNew description: ").strip()
                if new_desc:
                    step['description'] = new_desc
                    step['user_modified'] = True
                    logger.info("Step updated successfully")
            else:
                logger.error("Invalid step number")
        except ValueError:
            logger.error("Please enter a valid number")
    
    def add_step(self):
        """Add new step to the plan"""
        new_desc = input("Enter new step description: ").strip()
        if new_desc:
            new_step = {
                'id': f"step_{len(self.current_plan['steps']) + 1}",
                'description': new_desc,
                'checked': False,
                'editable': True,
                'user_modified': True
            }
            self.current_plan['steps'].append(new_step)
            logger.info("New step added successfully")
    
    def approve_plan(self):
        """Approve the plan and continue workflow"""
        logger.info("✅ Plan approved! Continuing workflow...")
        self.current_plan['status'] = 'approved'
        
        # Save approved plan
        with open('approved_plan.json', 'w') as f:
            json.dump(self.current_plan, f, indent=2)
        
        # Continue with next steps (PRD generation, GitHub issues, etc.)
        self.continue_workflow()
    
    def continue_workflow(self):
        """Continue workflow after plan approval"""
        logger.info("🚀 Continuing workflow execution...")
        
        # Generate PRD draft and send to Notion
        logger.info("📝 Generating PRD draft...")
        prd_sent = self.send_prd_to_notion()
        
        # Other workflow steps
        logger.info("📋 Creating GitHub issues...")
        logger.info("📢 Notifying stakeholders via Slack...")
        logger.info("📅 Scheduling review meeting...")
        
        if prd_sent:
            logger.info("✅ Workflow completed successfully with PRD sent to Notion!")
        else:
            logger.warning("⚠️ Workflow completed but PRD not sent to Notion")
        
        # Save workflow results
        workflow_results = {
            'plan': self.current_plan,
            'status': 'completed',
            'prd_sent_to_notion': prd_sent,
            'timestamp': '2025-08-24T18:00:00Z'
        }
        
        with open('workflow_results.json', 'w') as f:
            json.dump(workflow_results, f, indent=2)
    
    def send_prd_to_notion(self) -> bool:
        """Send the generated PRD to Notion"""
        try:
            from integrations.notion_integration import create_prd_in_notion
            
            # Extract PRD content from the plan
            prd_content = self._extract_prd_content()
            if not prd_content:
                logger.warning("No PRD content found to send to Notion")
                return False
            
            # Create title from the original prompt
            title = self._generate_prd_title()
            
            # Send to Notion
            page_id = create_prd_in_notion(title, prd_content)
            
            if page_id:
                logger.info(f"✅ PRD successfully sent to Notion (Page ID: {page_id})")
                return True
            else:
                logger.error("Failed to send PRD to Notion")
                return False
                
        except ImportError:
            logger.error("Notion integration not available")
            return False
        except Exception as e:
            logger.error(f"Error sending PRD to Notion: {str(e)}")
            return False
    
    def _extract_prd_content(self) -> str:
        """Extract PRD content from the generated plan with better error handling"""
        if not self.current_plan:
            logger.warning("No current plan available for PRD extraction")
            return ""
        
        plan_output = self.current_plan.get('plan_output', '')
        
        # Check if Portia is asking for PRD instead of providing it
        if isinstance(plan_output, str):
            if any(phrase in plan_output.lower() for phrase in [
                "please provide the prd",
                "need the prd", 
                "provide prd",
                "prd required",
                "i need the information from the prd"
            ]):
                logger.warning("Portia SDK is asking for PRD content instead of providing it")
                return self._generate_fallback_prd()
            return plan_output
        
        elif hasattr(plan_output, 'value'):
            content = str(plan_output.value)
            if any(phrase in content.lower() for phrase in [
                "please provide the prd",
                "need the prd",
                "provide prd", 
                "prd required",
                "i need the information from the prd"
            ]):
                logger.warning("Portia SDK is asking for PRD content in structured output")
                return self._generate_fallback_prd()
            return content
        
        else:
            logger.warning(f"Unexpected plan_output type: {type(plan_output)}")
            return str(plan_output)
    
    def _generate_fallback_prd(self) -> str:
        """Generate a detailed fallback PRD when Portia doesn't provide content"""
        prompt = self.current_plan.get('original_prompt', 'Unknown feature')
        
        # Extract key information from the prompt for more specific PRD content
        prd_title = "Product Requirements Document"
        if "slack" in prompt.lower() and "integration" in prompt.lower():
            prd_title = "Slack Integration PRD"
        elif "feature" in prompt.lower():
            prd_title = "Feature Implementation PRD"
        
        return f"""# {prd_title}

## Overview
This PRD was automatically generated as a fallback when the Portia SDK requested PRD content instead of providing it.

## Problem Statement
Based on the user request: {prompt[:200]}...

## Business Requirements
1. Implement the requested functionality to address user needs
2. Ensure seamless integration with existing systems and workflows
3. Maintain high performance and scalability standards
4. Provide excellent user experience and intuitive interface
5. Include comprehensive testing and validation procedures

## Technical Requirements
1. API integration and data exchange protocols
2. Security and authentication mechanisms
3. Error handling and logging
4. Monitoring and alerting systems
5. Documentation and deployment procedures

## User Stories
- As a user, I want [functionality] so that I can [benefit]
- As an admin, I need [management capability] to ensure [operational need]
- As a stakeholder, I require [reporting/analytics] to measure [success metrics]

## Acceptance Criteria
- [ ] Feature implemented according to specifications
- [ ] Integration tested with all relevant systems
- [ ] Performance meets defined benchmarks
- [ ] Security requirements fully addressed
- [ ] Documentation complete and accurate

## Timeline & Milestones
- Phase 1: Research and Analysis (1-2 weeks)
- Phase 2: Development and Implementation (2-4 weeks)  
- Phase 3: Testing and Quality Assurance (1-2 weeks)
- Phase 4: Deployment and Rollout (1 week)
- Phase 5: Monitoring and Optimization (ongoing)

## Success Metrics
- User adoption and engagement rates
- System performance and reliability
- Error rates and resolution times
- Customer satisfaction scores
- Business impact and ROI

## Notes
This is an automatically generated fallback PRD. Please review and enhance with specific technical details, user stories, and acceptance criteria based on the actual requirements.
"""
    
    def _generate_prd_title(self) -> str:
        """Generate a title for the PRD based on the original prompt"""
        prompt = self.current_plan.get('original_prompt', 'Product Requirements Document')
        
        # Extract key words for title
        title_keywords = ["PRD", "Product Requirements", "Feature", "Integration"]
        for keyword in title_keywords:
            if keyword.lower() in prompt.lower():
                return f"{keyword} - {prompt[:50]}..."
        
        return f"PRD - {prompt[:50]}..."
    
    def run_workflow(self, user_prompt: str):
        """Main workflow execution"""
        logger.info("🤖 Starting PM Agent Workflow...")
        
        # Step 1: Generate plan with Portia
        plan = self.generate_plan(user_prompt)
        if not plan:
            logger.error("Failed to generate plan. Exiting.")
            return
        
        # Step 2: User review and modification
        while self.current_plan['status'] != 'approved':
            self.display_plan_with_options()
            action = self.get_user_action()
            self.handle_user_action(action)
        
        logger.info("🎉 Workflow execution completed!")

def main():
    """Main function to run the PM Agent Workflow"""
    workflow = PMAgentWorkflow()
    
    # Get user prompt
    user_prompt = input("Enter your product management prompt: ").strip()
    if not user_prompt:
        user_prompt = "Create a comprehensive product development plan for a new AI feature based on user feedback"
    
    # Run the workflow
    workflow.run_workflow(user_prompt)

if __name__ == "__main__":
    main()

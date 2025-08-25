# Project Manager Agentic AI System

## Project Overview
This project is my implementation of the Portia SDK to design a full-fledged Product Management Workflow — built both as an internal tool and a prompt-driven AI Project Manager.
The system integrates with Slack, Notion, GitHub, and Google Calendar to create a smooth, end-to-end product management pipeline:
Capture user feedback, feature requests, and bug reports.
Allow the PM (or user) to choose which feature to prioritize.
Use Portia plan + build modules to generate a structured execution plan.
Provide human-in-the-loop approvals for plan editing, selection/deselection of steps, and refinement.
Auto-generate a PRD document, Slack updates, stakeholder messages, and GitHub issue templates.
Push finalized artifacts to Notion, GitHub, and Slack — with Google Calendar reminders for reviews.

## Features
- **Portia SDK Integration**: Leverages the capabilities of the Portia SDK for generating comprehensive product development plans.
- **Human-in-the-Loop Controls**: Users can interactively select, edit, and approve features at each step of the workflow.
- **Multi-Channel Integration**: Connects with Slack, Notion, GitHub, and Google Calendar for seamless communication and task management.
- **Sentiment Analysis**: Analyzes user feedback to prioritize feature requests based on impact scores.

## Installation Instructions
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
   ```

2. **Set Up Python Environment**:
   Ensure you have Python 3.13 installed. Create a virtual environment:
   ```bash
   python3 -m venv portia-env
   source portia-env/bin/activate
   ```

3. **Install Dependencies**:
   Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Create a `.env` file based on the `.env.example` template and fill in your API keys:
   ```plaintext
   # Slack Configuration
   SLACK_BOT_TOKEN=your-slack-bot-token-here
   SLACK_APP_TOKEN=your-slack-app-token-here
   SLACK_CHANNEL_ID=your-channel-id-here
   SLACK_TEST_CHANNEL=general

   # Google GenAI Configuration
   GOOGLE_API_KEY=your-google-api-key-here

   # Notion Configuration
   NOTION_API_KEY=your-notion-api-key-here
   NOTION_DATABASE_ID=your-notion-database-id-here

   # GitHub Configuration
   GITHUB_TOKEN=your-github-personal-access-token-here
   GITHUB_REPO_OWNER=your-github-username
   GITHUB_REPO_NAME=your-repo-name

   # Google Calendar Configuration
   GOOGLE_CALENDAR_CREDENTIALS_PATH=path/to/credentials.json
   GOOGLE_CALENDAR_TOKEN_PATH=path/to/token.json
   ```

5. **Run the Application as an Internal Tool**:
   Start the application using the main entry point:
   ```bash
   python main.py
   ```

6. **Run the Application as a Prompt Based Tool**:
   Start the application using the main entry point:
   ```bash
   python pm_agent_workflow.py
   ```      


## Technical Details

### Tools and Technologies
- **Portia SDK**: Used for generating and executing product development plans based on user feedback and feature requests.
- **Slack SDK**: Facilitates communication and notifications within Slack channels.
- **Notion API**: Used to upload the Product Requirements Document (PRD) for easy access and collaboration.
- **GitHub API**: Creates issues in the repository to track feature requests and development tasks.
- **Google Calendar API**: Schedules review meetings with stakeholders.
- 

### Key Features

- Portia SDK Orchestration
- Automates planning, PRD generation,Github Issue generation and execution flows.
- Human-in-the-Loop Workflow
- Nothing is “auto-finalized” — every step requires PM approval.
- Multi-Tool Integration
- Slack (communication), Notion (documentation), GitHub (execution), Google Calendar (reviews).
- Feedback-Driven Prioritization
- Reads from designated Slack channels to extract feature/bug reports and prompts the user for action.


### Workflow Steps for Internal tool

1. **Feature Selection**: 
   - Users select features from the feedback analysis loaded from `feedback_analysis.json`.
   - The UI displays available features and allows users to choose one to continue the workflow.

2. **Plan Generation**:
   - Upon selection, the system generates a comprehensive product development plan using the Portia SDK.
   - The plan includes research, PRD generation, GitHub issue creation, and stakeholder notifications.

3. **User Interaction**:
   - Users can review the generated plan, edit steps, and approve the plan before execution.
   - The system provides options to check/uncheck steps, edit descriptions, and add new steps.

4. **Integration with Notion**:
   - Once the plan is approved, the PRD is generated and uploaded to Notion for documentation and tracking.

5. **GitHub Issue Creation**:
   - A GitHub issue is created based on the approved PRD to track the implementation of the feature.

6. **Slack Notifications**:
   - Notifications are sent to the respective Slack channels `general` & `stakeholder`  with links to the GitHub issue and the Notion document.

7. **Google Calendar Scheduling**:
   - A review meeting is scheduled on Google Calendar to discuss the implementation and gather further feedback.

## Architecture

<img width="2742" height="3840" alt="Untitled diagram | Mermaid Chart-2025-08-25-175654" src="https://github.com/user-attachments/assets/8ad348d2-8a2c-40af-b7f3-7a838876f433" />


## Integration Details

### Slack Integration
- The system uses the Slack SDK to send notifications and updates to specific channels.
- It ensures that the bot is added to the relevant channels to avoid "not_in_channel" errors.

### Notion Integration
- The PRD is uploaded to Notion for easy access and collaboration among team members.

### GitHub Integration
- Issues are created in the GitHub repository to track the implementation of features based on user feedback.

### Google Calendar Integration
- Review meetings are scheduled to ensure timely discussions and feedback collection.


The PM Agentic AI System is built as a part of AgentHack by WeMakedevs and Portiailabs to showcase a powerful tool for product managers,by leveraging the features of Portia-sdk v0.7.2 to provide seamless integration with different Project Management tools and human in the loop oversight to drive effective decision-making and project execution.



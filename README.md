# PM Agentic AI System

## Project Overview
The PM Agentic AI System is designed to streamline product management workflows using the Portia SDK. This system integrates various tools and APIs to facilitate real-time feedback, feature selection, and project management, ensuring a human-in-the-loop approach at every step.

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

5. **Run the Application**:
   Start the application using the main entry point:
   ```bash
   python main.py
   ```

## Technical Details

### Tools and Technologies
- **Portia SDK**: Used for generating product development plans based on user feedback and feature requests.
- **Slack SDK**: Facilitates communication and notifications within Slack channels.
- **Notion API**: Used to upload the Product Requirements Document (PRD) for easy access and collaboration.
- **GitHub API**: Creates issues in the repository to track feature requests and development tasks.
- **Google Calendar API**: Schedules review meetings with stakeholders.

### Workflow Steps
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
   - Notifications are sent to the Slack channel `all-lystai` with links to the GitHub issue and the Notion document.

7. **Google Calendar Scheduling**:
   - A review meeting is scheduled on Google Calendar to discuss the implementation and gather further feedback.

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

## Conclusion
The PM Agentic AI System is a powerful tool for product managers, providing a seamless integration of AI capabilities with human oversight to drive effective decision-making and project execution.

---

This README provides a comprehensive overview of the project, installation instructions, and technical details. If you need any modifications or additional sections, please let me know!

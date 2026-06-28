# Streamline Your Workflow with Databricks FM and Streamlit Integration

## What This Is
This repository provides a solution for developers to integrate Databricks FM Opus 4.6 with Streamlit, creating an efficient and interactive chatbot. It leverages OAuth authentication via the Databricks SDK for a seamless user experience.

## Why It Matters
By simplifying authentication and harnessing the power of Databricks FM, this setup provides real-time chatbot interactions, maximizing productivity for developers and data scientists. The integration facilitates intuitive deployment and interaction with conversational AI models.

## Architecture Overview
The architecture flow includes:
- **Streamlit**: Used to develop the interactive chatbot interface.
- **Databricks SDK with OAuth**: Provides unified authentication to access the Databricks FM Opus 4.6, using WorkspaceClient(...).serving_endpoints.get_open_ai_client().

## Setup & Installation
To set up the environment, follow these steps:

### Authentication and Optional Configurations
1. **Authenticate using OAuth**:
   ```
   databricks auth login --host https://your-workspace.cloud.databricks.com
   ```

2. **Optional environment variables**:
   ```
   export DATABRICKS_CONFIG_PROFILE=my-profile        # Pick a named profile if needed
   export OPUS_ENDPOINT=databricks-claude-opus-4-6    # Endpoint, optional
   ```

### Installation and Run Command
3. Navigate to the app directory:
   ```
   cd app
   ```

4. Install required packages:
   ```
   pip install -r requirements.txt
   ```

5. Launch the application:
   ```
   streamlit run app.py
   ```

## What You'll See in the Demo
- **Interactive Chatbot Interface**: Engage in real-time conversations with the Opus 4.6 model.
- **Authorization Checks**: Experience seamless chatbot functionality along with gracious warnings if the user is not authenticated.

This integration showcases how modern AI technologies can be efficiently combined to deliver a robust and user-friendly chatbot application.

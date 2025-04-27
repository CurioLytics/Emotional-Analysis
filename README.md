# Journal Application

A personal journaling and self-reflection tool with AI-powered insights and emotional analysis.

## Features

- **Journal Entries**: Create and manage daily journal entries with easy date navigation
- **AI Chat**: Converse with an AI assistant that can recall information from your journal entries
- **Emotional Analysis**: Visualize emotional trends and patterns from your journal content
- **Multipage Interface**: Simple and intuitive navigation between different application features

## Architecture

This application uses a modern architecture that separates concerns:

- **Streamlit**: Handles the user interface and interactions
- **Supabase**: Provides the database backend for storing journal entries and analysis data
- **n8n**: Manages AI workflows, embeddings, and retrieval augmented generation (RAG)

## Getting Started

### Prerequisites

- Python 3.12+
- Access to a Supabase instance
- Access to n8n workflows for AI processing

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd journal-streamlit-app
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the root directory with the following variables:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   N8N_WEBHOOK_CHAT_URL=your_n8n_chat_webhook_url
   N8N_WEBHOOK_UPDATE_URL=your_n8n_update_webhook_url
   N8N_BEARER_TOKEN=your_n8n_bearer_token
   ```

### Running the Application

Start the Streamlit application:
```
streamlit run app.py
```

The application will be available at http://localhost:8501

## Application Structure

- `app.py`: Main entry point for the application
- `pages/`: Contains the individual application pages
  - `journal-page.py`: Journal entry creation and management
  - `chat-page.py`: AI chat interface
  - `analysis-page.py`: Emotional analysis visualizations
- `utils/`: Utility functions for the application
  - `auth.py`: Authentication and credential management
  - `webhook.py`: Communication with n8n webhooks
  - `database.py`: Database operations

## Data Model

The application uses a simple data model in Supabase:

- **documents**: Stores journal entries
  - `id`: UUID (primary key)
  - `content`: Text (journal content)
  - `date-entry`: Date (when the entry was created)
  - Additional fields for metadata and analysis

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Acknowledgments

- Streamlit for the wonderful UI framework
- Supabase for the backend database
- n8n for the workflow automation
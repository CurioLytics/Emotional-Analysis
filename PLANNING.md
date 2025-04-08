# Journal and Chat Application - Project Plan

## Project Overview

This application is a personal journaling and memory retrieval tool that allows users to:
1. Create and manage journal entries
2. Chat with an AI assistant that can access and recall information from their journal entries
3. Analyze the emotional content of journal entries with interactive visualizations
4. Utilize Retrieval-Augmented Generation (RAG) to enhance the quality of AI responses

## Technology Stack

### Frontend
- **Streamlit**: A Python library for building interactive web applications
  - Fast development cycles
  - Built-in UI components (forms, tables, chat interfaces)
  - Simple deployment options
  - Multipage application structure for organized navigation

### Backend & Database
- **Supabase**: An open-source Firebase alternative
  - PostgreSQL database for storage
  - Direct connection from Streamlit app for data operations
  - Authentication services (future implementation)

### AI Integration
- **n8n**: A workflow automation tool
  - Handles all AI-related tasks (embeddings, RAG, etc.)
  - Accessed via webhook endpoints from Streamlit
  - Integration with LLMs (currently using GPT-4o-mini)
  - Performs direct database operations to Supabase for AI tasks

### Workflow Architecture

```
┌─────────────────┐      ┌─────────────────┐      
│                 │      │                 │      
│    Streamlit    │◄────►│    Supabase     │      
│   Application   │      │    Database     │      
│                 │      │                 │      
└─────────────────┘      └─────────────────┘      
        │                        ▲                
        │                        │                
        ▼                        │                
┌─────────────────┐              │                
│                 │              │                
│      n8n        │──────────────┘                
│    Workflows    │                              
│                 │                              
└─────────────────┘                              
        │                                         
        │                                         
        ▼                                         
┌─────────────────┐                              
│                 │                              
│    LLM API      │                              
│                 │                              
└─────────────────┘                              
```

## Application Structure

### Main Application (app.py)
- Entry point for the multipage Streamlit application
- Provides application overview and navigation
- Displays basic statistics and welcome information

### Pages
1. **Journal Page** (pages/journal-page.py)
   - Create, view, and manage personal journal entries
   - Store entries in Supabase with proper date indexing
   - Simple, clean UI for easy journaling
   - Send data to n8n for AI processing via webhooks

2. **Chat Interface** (pages/chat-page.py)
   - Conversational interface to interact with the system
   - Session management to maintain context
   - Send user queries to n8n via webhooks and display responses
   - Typing effect for improved user experience

3. **Journal Analysis** (pages/analysis-page.py)
   - Display emotional analysis data from journal entries
   - Visualize emotion scores and trends over time
   - Provide insights into emotional patterns
   - Retrieve analysis data from Supabase (processed by n8n)

### Utilities
- **auth.py**: Authentication and credential management
- **webhook.py**: Communication with n8n webhooks
- **database.py**: Supabase database operations

### RAG System (handled entirely by n8n) -> no need to code here
- Vector embeddings of journal content (managed by n8n)
- Similarity search functionality (executed within n8n)
- Context-aware responses from LLM (processed by n8n)
- Direct database operations from n8n to Supabase

## Current Implementation Status

- Core functionality for all three main pages is implemented
- Webhook integration with n8n is functional
- Multipage application structure is complete
- Basic visualization for emotional analysis is in place
- Journal entry creation and listing is working
- Chat interface with AI assistant is operational

## Implementation Approach

### Phase 1: Core Functionality (Completed)
- Journal entry creation and listing
- Basic chat interface
- Webhook connections to n8n workflows
- Multipage application structure

### Phase 2: Authentication & User Management (Next)
- Implement user authentication via Supabase
- User profile management
- Secure data access controls

### Phase 3: Enhanced Features
- UI/UX improvements for journal and chat
- Advanced search and filtering
- Mobile responsiveness improvements

### Phase 4: Polish & Production
- UI/UX improvements
- Performance optimization
- Comprehensive testing
- Production deployment

## Data Model

### Journal Entries (documents table)
- `id`: UUID (primary key)
- `content`: Text (journal content)
- `date-entry`: Date (when the entry was about)
- `file-url`: Text (optional link to related file)

Note: Vector embeddings and AI-related data fields are managed directly by n8n workflows.

## Technical Constraints & Considerations

1. **Security**: Ensure proper authentication and data privacy
2. **Separation of Concerns**: Streamlit app handles UI and basic data operations, n8n handles all AI tasks
3. **User Experience**: Keep the interface simple and intuitive
4. **Webhook Management**: Ensure reliable communication between Streamlit and n8n

## Next Steps

See the accompanying TASK.md file for specific implementation tasks and their priorities.
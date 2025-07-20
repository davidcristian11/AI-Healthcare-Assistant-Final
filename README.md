# Smart Healthcare Assistant

A web-based AI platform that provides real-time medical information through natural conversation and image analysis. Featuring Retrieval Augmented Generation (RAG) technology, it delivers reliable healthcare guidance by accessing a dynamic knowledge base that healthcare professionals can update.

## Features

- **Real-time RAG Integration**: Leverages Retrieval Augmented Generation for up-to-date, accurate medical information
- **Medical Professional Collaboration**: Healthcare providers can upload and modify medical documents in real-time
- **Conversational Interface**: Engage in natural dialogue with an AI trained on medical knowledge
- **Medical Image Analysis**: Upload and analyze MRIs, X-rays, and other medical imaging
- **Knowledge Base Integration**: Access information from 139+ specialized medical documents
- **Administrative Tools**: Manage the knowledge base through a simple interface
- **Responsive Design**: User-friendly interface that works on desktop and mobile devices

## Technology Stack

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python, Flask
- **AI**: Azure OpenAI GPT-4o
- **RAG System**: Custom keyword-based retrieval system for real-time document integration
- **Image Analysis**: Azure Vision capabilities

## Getting Started

### Prerequisites

- Python 3.9+
- Azure OpenAI API key with access to GPT-4o
- Flask and required packages

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/cris192511/ai_healthcare_assistant
   cd smart-healthcare-assistant
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables
   ```bash
   cp .env.example .env
   # Edit .env file with your Azure API credentials
   ```

4. Run the application
   ```bash
   python app.py
   ```

5. Visit `http://127.0.0.1:5000/` in your browser

## Project Structure

```
smart-healthcare-assistant/
├── app.py                  # Main Flask application
├── ai_service.py           # Basic AI response handling
├── image_service.py        # Image analysis functionality
├── knowledge_base.py       # Document storage and retrieval
├── knowledge/              # Medical document storage
├── static/                 # CSS, JavaScript, and static files
├── templates/              # HTML templates
├── uploads/                # Temporary image storage
└── requirements.txt        # Python dependencies
```

## Usage

### Chat Interface

Ask questions about symptoms, conditions, treatments, or general health advice. The AI will respond with relevant information from its knowledge base in real-time.

### Image Analysis

Upload medical images like MRIs or X-rays by clicking the image icon in the chat interface. Ask specific questions about the uploaded image.

### Knowledge Management for Healthcare Providers

Healthcare professionals can access the admin interface at `/admin` to add, edit, or manage documents in the knowledge base. This allows for real-time updates to medical information as new research or guidelines become available.

## Rate Limiting

The application includes robust handling for API rate limits:
- Detects when Azure API quotas are reached
- Provides fallback responses using keyword-based document retrieval
- Resumes full AI capabilities automatically when limits reset

## Contributors

- Strîmbu David-Cristian
- Pop Raul Bogdan
- Popa Samuel Paul

## Disclaimer

This application provides general health information and is not a substitute for professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare providers for medical concerns.

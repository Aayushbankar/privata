# MOSDAC AI Help Bot

An AI-powered help bot for the MOSDAC (Meteorological & Oceanographic Satellite Data Archival Centre) portal developed for Space Applications Centre ISRO. This system provides intelligent information retrieval from the vast MOSDAC website content using Natural Language Processing and Machine Learning techniques.

## 🌟 Features

- **AI-Powered Chat Interface**: Natural language queries with intelligent responses
- **Real-time Information Retrieval**: Continuous scanning and indexing of MOSDAC website content
- **Context Awareness**: Maintains conversation context within sessions
- **Source Citation**: Provides sources with relevance scores for transparency
- **Self-Learning Capabilities**: Improves responses based on user interactions
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices

## 🏗️ Architecture

The system consists of three main components:

1. **Backend API** (`main.py`): FastAPI server handling AI processing and database operations
2. **Frontend Interface** (`frontend/`): Modern web interface for user interaction
3. **Data Processing** (`src/`): Scraping, ingestion, and vector database management

## 🚀 Quick Start

### Option 1: Unified Launcher (Recommended)

```bash
# Make the launcher executable
chmod +x run_app.py

# Start both backend and frontend
python run_app.py

# Or with custom ports
python run_app.py --api-port 8000 --frontend-port 3000
```

This will:
- Start the FastAPI backend on port 8000
- Serve the frontend on port 3000
- Open your browser automatically
- Provide monitoring and automatic restart capabilities

### Option 2: Manual Setup

```bash
# Start the backend API
python main.py

# In another terminal, start the frontend server
cd frontend
python -m http.server 3000
```

Then open `http://localhost:3000` in your browser.

## 📁 Project Structure

```
privata/
├── frontend/                 # Web interface
│   ├── index.html           # Main HTML file
│   ├── styles.css           # Styling and responsive design
│   ├── script.js            # JavaScript functionality
│   └── README.md            # Frontend documentation
├── src/                     # Core application code
│   ├── api/                 # FastAPI backend
│   ├── chat/                # Chat processing logic
│   ├── ingestion/           # Data ingestion pipelines
│   ├── models/              # LLM loading and management
│   ├── retrieval/           # Vector database and search
│   ├── scrapers/            # Web scraping utilities
│   └── utils/               # Utility functions
├── data/                    # Scraped data and databases
├── config/                  # Configuration files
├── docs/                    # Documentation
├── main.py                  # Main FastAPI application
├── run_app.py              # Unified application launcher
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🔧 API Endpoints

The backend provides the following API endpoints:

- `POST /api/v1/chat` - Process chat messages and return AI responses
- `GET /api/v1/status` - Get system status and statistics
- `GET /docs` - Interactive API documentation (Swagger UI)

### Chat Request Format:
```json
{
  "query": "What is MOSDAC?",
  "session_id": "unique_session_id"
}
```

### Chat Response Format:
```json
{
  "response": "MOSDAC is the Meteorological & Oceanographic Satellite Data Archival Centre...",
  "sources": [
    {
      "url": "https://mosdac.gov.in/about",
      "title": "About MOSDAC",
      "relevance": 0.95,
      "content": "Content snippet..."
    }
  ]
}
```

## 🎯 Example Questions

The frontend includes example questions to help users get started:

- "What is MOSDAC and what does it do?"
- "How can I access satellite data from MOSDAC?"
- "What types of meteorological data are available?"
- "Tell me about INSAT-3D satellite capabilities"
- "How does MOSDAC handle data quality?"

## 🛠️ Development

### Prerequisites

- Python 3.8+
- Modern web browser
- Internet connection (for external API calls)

### Installation

1. Clone the repository
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Ensure the backend data has been scraped and processed

### Running in Development Mode

```bash
# Using the unified launcher (recommended)
python run_app.py

# Or manually
# Terminal 1: Backend
python main.py

# Terminal 2: Frontend
cd frontend
python -m http.server 3000
```

## 📊 System Status

The frontend displays real-time system information:

- **Scraped Pages**: Number of pages processed from MOSDAC
- **Vector Database**: Status of the search database
- **LLM Status**: Availability of the language model
- **Last Update**: When the system was last updated

## 🔒 Security Features

- Input sanitization to prevent XSS attacks
- CORS configuration for secure cross-origin requests
- No sensitive data storage in the frontend
- Secure API communication

## 🌐 Browser Support

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## 📝 License

This project is developed for Space Applications Centre ISRO as part of the problem statement PS000007.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 🐛 Troubleshooting

### Common Issues:

1. **Backend not starting**: Check if all dependencies are installed
2. **CORS errors**: Ensure backend allows requests from frontend origin
3. **API connection issues**: Verify backend is running on correct port
4. **Frontend not loading**: Check if frontend server is running

### Debug Mode:

Enable debug logging by setting environment variables:
```bash
export DEBUG=true
export LOG_LEVEL=debug
```

## 📞 Support

For technical support or issues, please check:
- API documentation at `http://localhost:8000/docs`
- Browser developer console for JavaScript errors
- Backend server logs for API issues

---

**Developed for Space Applications Centre ISRO** 🛰️

*Empowering citizens with intelligent access to satellite data and information.*

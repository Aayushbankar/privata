# MOSDAC AI Help Bot Frontend

A modern, responsive web interface for the MOSDAC AI Help Bot system developed for Space Applications Centre ISRO.

## Features

### 🚀 Core Functionality
- **AI-Powered Chat Interface**: Natural language conversations with the MOSDAC AI assistant
- **Real-time Information Retrieval**: Instant responses based on scraped MOSDAC website content
- **Session Management**: Context-aware conversations with session persistence
- **Source Attribution**: Transparent display of information sources with relevance scoring

### 🎨 User Experience
- **Modern UI Design**: Clean, professional interface with gradient backgrounds and glassmorphism effects
- **Responsive Design**: Fully responsive layout that works on desktop, tablet, and mobile devices
- **Real-time Status Indicators**: System health monitoring with visual status indicators
- **Typing Animation**: Visual feedback when the AI is processing responses
- **Example Questions**: Quick-start buttons with common MOSDAC-related queries

### 📊 System Information Panel
- **Scraped Pages Counter**: Shows total number of pages processed from MOSDAC website
- **Vector Database Status**: Displays document count and last update timestamp
- **LLM Availability**: Real-time status of the language model service
- **System Health**: Continuous monitoring of backend API connectivity

### 🔍 Advanced Features
- **Source Modal**: Detailed view of information sources with relevance percentages
- **Keyboard Shortcuts**: Press `/` to quickly focus the chat input
- **Error Handling**: Graceful error handling with user-friendly messages
- **Session Persistence**: Maintains conversation context within a browsing session

## Technical Architecture

### Frontend Stack
- **HTML5**: Semantic markup with modern web standards
- **CSS3**: Advanced styling with Flexbox, Grid, and CSS animations
- **Vanilla JavaScript**: No framework dependencies for optimal performance
- **Google Fonts**: Roboto font family for clean typography

### API Integration
- **RESTful API**: Communication with FastAPI backend
- **CORS Enabled**: Proper cross-origin resource sharing configuration
- **WebSocket Ready**: Architecture supports real-time updates if needed

### Performance Features
- **Lazy Loading**: Efficient resource loading
- **CSS Animations**: Hardware-accelerated smooth animations
- **Optimized Images**: SVG icons for crisp rendering at any resolution
- **Efficient DOM Manipulation**: Minimal reflows and repaints

## Installation & Setup

### Prerequisites
- Python 3.7+ installed
- Backend API server running on port 8000

### Quick Start
1. Ensure the backend is running:
   ```bash
   python run_app.py
   ```

2. The frontend will automatically be served on http://localhost:3000

### Manual Setup
If you want to run the frontend separately:

```bash
cd frontend
python -m http.server 3000
```

### Development Mode
For development with auto-reload:

```bash
# Using the unified launcher (recommended)
python run_app.py --port 3000 --api-port 8000

# Or manually
cd frontend && python -m http.server 3000
```

## Configuration

### API Endpoint
The frontend connects to the API endpoint configured in `script.js`:
```javascript
this.API_BASE_URL = 'http://localhost:8000/api/v1';
```

### Environment Variables
For production deployment, you can configure:
- `API_BASE_URL`: Backend API endpoint URL
- `FRONTEND_PORT`: Port for the HTTP server

## Usage

### Basic Interaction
1. Open http://localhost:3000 in your web browser
2. Type your question in the chat input field
3. Press Enter or click the send button
4. View the AI response with source attribution

### Example Questions
Use the pre-configured example buttons to quickly ask about:
- INSAT-3D satellite information
- Weather forecasting capabilities
- Ocean surface current data
- Agricultural satellite products

### Source Inspection
- Click on any source in the chat to view detailed information
- The modal shows relevance scores and content excerpts
- Sources are sorted by relevance percentage

## Customization

### Styling
Modify `styles.css` to customize:
- Color scheme and gradients
- Typography and spacing
- Component sizes and layouts
- Animation timing and effects

### Functionality
Extend `script.js` to add:
- Additional API endpoints
- Custom UI components
- Enhanced error handling
- Additional keyboard shortcuts

## Browser Support

- **Chrome**: 60+ (full support)
- **Firefox**: 55+ (full support)
- **Safari**: 12+ (full support)
- **Edge**: 79+ (full support)
- **Mobile Browsers**: iOS Safari 12+, Chrome Mobile 60+

## Performance Metrics

- **First Contentful Paint**: < 1s
- **Time to Interactive**: < 2s
- **Bundle Size**: ~15KB (HTML + CSS + JS)
- **API Response Time**: Dependent on backend processing

## Security Features

- **XSS Protection**: Input sanitization and output escaping
- **CSP Ready**: Content Security Policy compatible
- **HTTPS Compatible**: Secure communication support
- **No External Dependencies**: Reduced attack surface

## Monitoring & Analytics

The frontend includes:
- System status monitoring
- API connectivity checks
- Error logging to console
- Performance timing measurements

## Deployment

### Production Build
For production deployment:

1. Minify CSS and JavaScript
2. Configure proper CORS headers
3. Set up HTTPS encryption
4. Configure proper API endpoint URLs

### Docker Deployment
Example Dockerfile:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY frontend/ .
EXPOSE 3000
CMD ["python", "-m", "http.server", "3000"]
```

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure backend has proper CORS configuration
2. **API Connection Failed**: Verify backend is running on port 8000
3. **Static File Issues**: Check file permissions in the frontend directory

### Debug Mode
Enable console logging by setting:
```javascript
console.debug = true;
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is developed for Space Applications Centre ISRO as part of the AI-based Help Bot initiative.

## Support

For technical support or questions about the frontend:
- Check the browser console for error messages
- Verify backend API connectivity
- Review the network tab for API requests

---

**Built for Space Applications Centre ISRO - Advancing Space Technology through AI Innovation**

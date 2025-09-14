# MOSDAC AI Help Bot Frontend

A modern, responsive web interface for the MOSDAC AI Help Bot system built for Space Applications Centre ISRO.

## Features

- **Real-time Chat Interface**: Clean, modern chat interface with message bubbles
- **Source Citation**: View and click through information sources with relevance scores
- **System Status Monitoring**: Live system status indicators and statistics
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Example Questions**: Quick-start buttons with common queries
- **Typing Indicators**: Visual feedback when AI is processing requests
- **Session Management**: Persistent conversation sessions
- **Error Handling**: Graceful error handling and user feedback

## Technology Stack

- **HTML5**: Semantic markup structure
- **CSS3**: Modern styling with gradients, animations, and responsive design
- **JavaScript ES6+**: Vanilla JavaScript with modern features
- **Google Fonts**: Roboto font family for clean typography
- **Fetch API**: Modern API communication

## API Integration

The frontend communicates with the backend API at `http://localhost:8000/api/v1`:

### Endpoints Used:
- `POST /api/v1/chat` - Send chat messages and receive responses
- `GET /api/v1/status` - Check system status and statistics

### Request Format:
```json
{
  "query": "user message",
  "session_id": "unique_session_id"
}
```

### Response Format:
```json
{
  "response": "AI generated response",
  "sources": [
    {
      "url": "https://mosdac.gov.in/page",
      "title": "Page Title",
      "relevance": 0.95,
      "content": "Extracted content snippet..."
    }
  ]
}
```

## Installation & Setup

1. **Ensure Backend is Running**: The FastAPI backend must be running on `localhost:8000`

2. **Open Frontend**: Simply open `frontend/index.html` in a web browser

3. **Alternative Serving**: For better development experience, serve via HTTP server:
   ```bash
   # Using Python
   cd frontend
   python -m http.server 3000
   
   # Using Node.js (if you have http-server installed)
   npx http-server -p 3000
   ```

## File Structure

```
frontend/
├── index.html          # Main HTML structure
├── styles.css          # All styling and responsive design
├── script.js          # JavaScript functionality and API integration
└── README.md          # This file
```

## Browser Support

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## Key Features Explained

### 1. Chat Interface
- Message bubbles with different styles for user and bot
- Timestamps for all messages
- Smooth scrolling and animations
- Auto-focus on input field

### 2. Source Management
- Clickable source citations with relevance percentages
- Modal popup for detailed source information
- Direct links to original MOSDAC content

### 3. System Monitoring
- Real-time status indicators (online/offline)
- Statistics about scraped pages and database status
- Automatic status checks every minute

### 4. User Experience
- Typing indicators with animated dots
- Example questions for quick starts
- Keyboard shortcuts (press '/' to focus input)
- Error handling with user-friendly messages

## Customization

### Styling
Modify `styles.css` to customize:
- Color scheme (gradient backgrounds)
- Typography (font sizes, weights)
- Layout (grid proportions, spacing)
- Animations and transitions

### API Configuration
Change API base URL in `script.js`:
```javascript
this.API_BASE_URL = 'http://your-api-url:port/api/v1';
```

### Example Questions
Add more example questions in `index.html`:
```html
<button class="example-btn" data-question="Your question here">
    Button Text
</button>
```

## Performance Features

- **Lazy Loading**: Resources load as needed
- **Efficient DOM Updates**: Minimal re-rendering
- **Debounced API Calls**: Prevents rapid-fire requests
- **Local Storage**: Optional session persistence (can be added)

## Security Considerations

- XSS protection through input sanitization
- CORS handling (ensure backend allows frontend origin)
- No sensitive data storage in frontend

## Development Notes

- Built with vanilla JavaScript for minimal dependencies
- Uses modern CSS features (Grid, Flexbox, CSS Variables)
- Follows accessibility best practices
- Includes comprehensive error handling

## Troubleshooting

1. **CORS Errors**: Ensure backend allows requests from your frontend origin
2. **API Connection**: Verify backend is running on `localhost:8000`
3. **Styling Issues**: Check browser compatibility for CSS features
4. **JavaScript Errors**: Open browser console to debug issues

## Future Enhancements

- [ ] Local storage for conversation history
- [ ] File upload support
- [ ] Voice input/output
- [ ] Multi-language support
- [ ] Advanced filtering and search
- [ ] User authentication
- [ ] Conversation export
- [ ] Dark/light theme toggle

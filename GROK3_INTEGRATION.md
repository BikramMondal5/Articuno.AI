# Grok-3 Integration for Articuno.AI

This document describes the integration of Grok-3 bot into the Articuno.AI web application.

## Overview

Grok-3 is now integrated into the Articuno.AI platform as a selectable bot in the sidebar. Users can interact with Grok-3 directly through the web interface instead of using the terminal.

## What Was Changed

### 1. **agent/grok3.py** - Modified
- Added `get_grok3_response(user_message)` function for web application integration
- Function accepts a user message and returns the AI response
- Maintains the same Azure AI Inference client setup
- Added proper error handling
- Added a comprehensive system prompt defining Grok-3's personality and capabilities
- Terminal testing functionality still available when running the script directly

### 2. **app.py** - Updated
- Imported the `get_grok3_response` function from `agent.grok3`
- Added `process_grok3_request(user_input)` function to handle Grok-3 requests
- Updated the `/api/chat` route to handle "Grok-3" bot selection
- Follows the same pattern as GPT-4o-mini and Wikipedia Bot

### 3. **templates/index.html** - Updated
- Added Grok-3 bot item to the sidebar bots list
- Bot appears between GPT-4o-mini and DeepSeek R1
- Uses `grok3-avatar` as the avatar ID

### 4. **static/script.js** - Updated
- Added Grok-3 entry to the `botDescriptions` object
- Includes description: "xAI's advanced AI assistant with a witty personality..."
- References `icons/grok-logo.png` for the avatar

### 5. **static/styles.css** - Updated
- Added `#grok3-avatar` styling
- Includes fallback text "G3" if logo image is not available
- Consistent with other bot avatar styles

### 6. **static/icons/GROK_ICON_INFO.md** - New File
- Instructions for adding the Grok logo image
- Temporary workaround suggestions if logo is unavailable

## Features

### Grok-3 Personality
- Witty and intelligent responses
- Slight rebellious edge with appropriate humor
- Challenges assumptions when appropriate
- Uses markdown formatting for better readability
- Includes emojis for enhanced engagement

### How It Works
1. User clicks on "Grok-3" in the sidebar
2. Chatbot showcase displays Grok-3 information
3. User can start chatting by clicking "Start Analysing"
4. Messages are sent to `/api/chat` endpoint with `bot: "Grok-3"`
5. Backend calls `get_grok3_response()` function
6. Response is converted from markdown to HTML
7. Response is displayed in the chat interface

## Requirements

- `GITHUB_TOKEN` environment variable must be set in `.env` file
- Token must have access to GitHub Models (Grok-3)
- All existing dependencies remain the same

## Testing

### Test in Terminal (Original Functionality)
```bash
cd agent
python grok3.py
```

### Test in Web Application
1. Start the Flask server: `python app.py`
2. Open browser to `http://localhost:5000`
3. Click on "Grok-3" in the sidebar
4. Click "Start Analysing"
5. Type a message and press send

## Adding the Grok Logo

To complete the visual integration:

1. Download or create a Grok/xAI logo (preferably PNG with transparent background)
2. Save as `grok-logo.png` in the `static/icons/` directory
3. Recommended size: 512x512 pixels
4. Restart the Flask server if needed

If no logo is added, the avatar will show "G3" as a text fallback.

## Integration Pattern

This integration follows the same pattern as other bots in the application:

```
User Input → Frontend (script.js) 
          → Backend Route (/api/chat) 
          → Bot Handler (process_grok3_request)
          → Agent Function (get_grok3_response)
          → AI Model (Grok-3 via GitHub Models)
          → Response → Markdown to HTML
          → Display in Chat Interface
```

## Troubleshooting

### Bot Not Appearing in Sidebar
- Check that the HTML was updated correctly
- Clear browser cache
- Restart Flask server

### "Grok-3 is currently unavailable" Error
- Verify `GITHUB_TOKEN` is set in `.env` file
- Check token has access to GitHub Models
- Review console logs for import errors

### Response Not Displaying
- Check browser console for JavaScript errors
- Verify backend logs for errors in `process_grok3_request`
- Ensure markdown conversion is working

## Future Enhancements

Potential improvements:
- Add conversation history support
- Implement streaming responses
- Add custom temperature/parameter controls
- Support for image inputs (multimodal capabilities)
- Rate limiting and usage tracking

## Credits

- **Grok-3**: Developed by xAI (Elon Musk's AI company)
- **Integration**: Articuno.AI Development Team
- **Platform**: GitHub Models via Azure AI Inference

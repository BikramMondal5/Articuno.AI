# Wikipedia Bot Integration - Complete Guide

## ✅ What Has Been Done

I've successfully integrated your Wikipedia agent into the Articuno.AI web application! Here's what was changed:

### 1. **Modified `agent/wikipedia_agent.py`**
   - Converted from terminal-based script to web-compatible module
   - Added `get_wikipedia_response(user_query)` function for web integration
   - Kept the LangChain agent with Wikipedia search tool
   - Improved system prompt for better Wikipedia-focused responses
   - Terminal testing capability remains (when run directly with `python wikipedia_agent.py`)

### 2. **Updated `app.py` (Flask Backend)**
   - Imported the Wikipedia agent: `from agent.wikipedia_agent import get_wikipedia_response`
   - Added new function `process_wikipedia_request()` to handle Wikipedia bot queries
   - Integrated Wikipedia Bot into the `/api/chat` endpoint
   - When user selects "Wikipedia Bot", queries are routed to the Wikipedia agent

### 3. **Updated `templates/index.html`**
   - Added "Wikipedia Bot" to the sidebar bot list
   - Positioned between "Gemini 2.0 Flash" and other bots
   - Uses `wikipedia-avatar` ID for styling

### 4. **Updated `static/script.js`**
   - Added Wikipedia Bot to `botDescriptions` object
   - Description: "Your intelligent Wikipedia search assistant powered by LangChain"
   - Bot automatically shows in showcase when clicked
   - All chat functionality integrated seamlessly

### 5. **Updated `static/styles.css`**
   - Added styling for `#wikipedia-avatar` in multiple places
   - Consistent with other bot avatars
   - Supports both sidebar and showcase displays

## 🎯 How It Works

### User Flow:
1. **User clicks "Wikipedia Bot"** in the left sidebar
2. **Showcase page appears** with bot description
3. **User starts chatting** by typing a query
4. **Query is sent** to Flask backend (`/api/chat`)
5. **Backend routes** to `process_wikipedia_request()`
6. **Wikipedia agent** searches Wikipedia using LangChain
7. **Response returned** and displayed in web interface

### Example Queries Users Can Ask:
- "Tell me about the Eiffel Tower"
- "What happened in World War 2?"
- "Give me information about Python programming language"
- "Who is Albert Einstein?"
- "Explain quantum physics"

## 📋 What You Need to Do

### 1. **Add Wikipedia Logo Icon** (Required)
You need to add a Wikipedia logo image file:

**File needed:** `static/icons/wikipedia-logo.png`

**Quick options:**
- **Option A**: Download from [Wikipedia Commons](https://commons.wikimedia.org/wiki/File:Wikipedia-logo-v2.svg)
- **Option B**: Search Google for "wikipedia icon png" and download
- **Option C**: Use the text-based placeholder (see instructions in `WIKIPEDIA_ICON_INFO.md`)

### 2. **Install Required Python Packages** (If Not Already Installed)
Make sure these packages are in your environment:
```bash
pip install langchain langchain-google-genai langchain-community wikipedia
```

### 3. **Verify Your `.env` File**
Ensure you have the Gemini API key (already configured for your other bots):
```
GEMINI_API_KEY=your_gemini_api_key_here
```

## 🚀 Testing the Integration

### Method 1: Test via Web Interface
1. Run the Flask app: `python app.py`
2. Open browser to `http://localhost:5000`
3. Click "Wikipedia Bot" in the sidebar
4. Type a query like "Tell me about the Moon"
5. You should see Wikipedia-sourced information!

### Method 2: Test Wikipedia Agent Directly (Terminal)
To verify the agent works independently:
```bash
python agent/wikipedia_agent.py
```
This will run a test query and print results to the terminal.

## 🎨 Customization Options

### Change Bot Name or Description
Edit `static/script.js`:
```javascript
"Wikipedia Bot": {
    name: "Wikipedia Bot",  // Change this
    description: "Your new description here",  // Change this
    avatar: "icons/wikipedia-logo.png"
}
```

### Change System Prompt
Edit `agent/wikipedia_agent.py`:
```python
agent = create_agent(
    model, 
    tools,
    system_prompt="Your custom prompt here"  # Change this
)
```

### Add More Tools to Wikipedia Agent
In `agent/wikipedia_agent.py`, you can add more tools:
```python
@tool
def another_tool(query: str) -> str:
    """Description of what this tool does"""
    # Your tool logic here
    return result

tools = [search_wikipedia, another_tool]  # Add to tools list
```

## 🐛 Troubleshooting

### "Import could not be resolved" Errors
- These are linting errors and won't affect functionality
- Install missing packages: `pip install langchain langchain-google-genai langchain-community wikipedia`

### Wikipedia Bot Not Showing in Sidebar
- Clear browser cache and refresh
- Check browser console for JavaScript errors (F12)

### "Wikipedia Agent error" When Sending Messages
- Check that Gemini API key is set in `.env`
- Verify Wikipedia agent imports correctly: `python -c "from agent.wikipedia_agent import get_wikipedia_response; print('OK')"`

### Icon Not Displaying
- Add `wikipedia-logo.png` to `static/icons/` folder
- Or use the text-based placeholder (see `WIKIPEDIA_ICON_INFO.md`)
- Clear browser cache after adding icon

## 📁 File Structure
```
Articuno.AI/
├── agent/
│   └── wikipedia_agent.py          ✅ Modified - Web-compatible
├── static/
│   ├── icons/
│   │   ├── wikipedia-logo.png      ⚠️ You need to add this
│   │   └── WIKIPEDIA_ICON_INFO.md  ℹ️ Instructions for icon
│   ├── script.js                   ✅ Updated - Bot integrated
│   └── styles.css                  ✅ Updated - Styling added
├── templates/
│   └── index.html                  ✅ Updated - Bot in sidebar
├── app.py                          ✅ Updated - API endpoint added
└── requirements.txt                ℹ️ May need to add packages
```

## ✨ Features of Your Wikipedia Bot

1. **Intelligent Search**: Uses LangChain to intelligently search Wikipedia
2. **Conversational Responses**: Formats Wikipedia info in friendly language
3. **Tool-based Architecture**: Can be extended with more tools
4. **Gemini-Powered**: Uses Google's Gemini 2.0 Flash for natural language
5. **Web Integration**: Seamlessly integrated into your existing UI
6. **Citation Support**: Agent mentions using Wikipedia as source

## 🎉 You're All Set!

Your Wikipedia bot is now integrated and ready to use. Just add the Wikipedia icon image, and you're good to go!

### Quick Start Commands:
```bash
# Install any missing dependencies
pip install langchain langchain-google-genai langchain-community wikipedia

# Test the agent directly
python agent/wikipedia_agent.py

# Run the web app
python app.py
```

Then visit `http://localhost:5000`, click on "Wikipedia Bot", and start asking questions!

---

**Need Help?** Check the troubleshooting section above or examine the code comments in the modified files.

# Quick Start: MongoDB Integration

## Step 1: Install MongoDB

### Windows
1. Download MongoDB Community Server: https://www.mongodb.com/try/download/community
2. Run the installer with default settings
3. MongoDB will start automatically as a Windows service

### Quick Verification
```bash
mongosh
```
If this opens the MongoDB shell, you're good to go!

## Step 2: Start Your Application

1. **Ensure MongoDB is running:**
   ```bash
   # Check if MongoDB service is running (Windows)
   net start MongoDB
   
   # Or manually start MongoDB
   mongod --dbpath C:\data\db
   ```

2. **Update your .env file:**
   ```env
   MONGODB_URI=mongodb://127.0.0.1:27017/
   SECRET_KEY=generate-a-random-string-here
   ```

3. **Run the Flask app:**
   ```bash
   python app.py
   ```

4. **Open your browser:**
   ```
   http://127.0.0.1:5000
   ```

## Step 3: Using the Features

### Creating Sessions
- A new session is automatically created when you start chatting
- Click the **"+"** button in the sidebar to manually create a new session
- Each session gets a unique ID for tracking

### Viewing History
- **Recent Sessions** appear in the left sidebar
- Click any session to restore its conversation history
- Sessions show the bot name, message count, and time ago

### Managing Sessions
- Hover over a session to see the delete button (trash icon)
- Delete unwanted sessions to keep your history clean
- Active session is highlighted with a purple gradient

### Searching Messages
- Use the search endpoint to find specific messages:
  ```javascript
  // From browser console
  fetch('/api/search?q=weather').then(r => r.json()).then(console.log)
  ```

## Step 4: Verify Everything Works

### Test MongoDB Connection
```bash
# Open MongoDB shell
mongosh

# Switch to database
use ArticunoAI

# Check collections
show collections

# View sessions
db.sessions.find().pretty()

# View messages
db.messages.find().pretty()
```

### Test in Browser
1. Open DevTools Console (F12)
2. Run:
   ```javascript
   // Check if sessionManager is loaded
   console.log(sessionManager);
   
   // List sessions
   sessionManager.listSessions().then(console.log);
   ```

## Troubleshooting

### "No module named 'pymongo'"
```bash
pip install pymongo==4.6.1
```

### "Failed to connect to MongoDB"
1. Check MongoDB is running:
   ```bash
   net start MongoDB  # Windows
   sudo systemctl start mongod  # Linux
   ```

2. Check port 27017 is not blocked:
   ```bash
   netstat -an | findstr 27017
   ```

### "sessionManager is not defined"
1. Check browser console for errors
2. Verify `session_manager.js` is loaded before `script.js`
3. Hard refresh (Ctrl+Shift+R)

### Sessions not appearing
1. Clear browser cache
2. Check MongoDB has data:
   ```bash
   mongosh
   use ArticunoAI
   db.sessions.count()
   ```

## Quick Commands Reference

### MongoDB Commands
```javascript
// Show all databases
show dbs

// Use ArticunoAI database
use ArticunoAI

// Count documents
db.sessions.count()
db.messages.count()

// Find recent sessions
db.sessions.find().sort({last_activity: -1}).limit(5)

// Delete all sessions (CAUTION!)
db.sessions.deleteMany({})
db.messages.deleteMany({})
```

### API Testing with cURL
```bash
# Create new session
curl -X POST http://localhost:5000/api/session/new \
  -H "Content-Type: application/json" \
  -d '{"bot": "Articuno.AI"}'

# List sessions
curl http://localhost:5000/api/session/list

# Search messages
curl http://localhost:5000/api/search?q=weather
```

## Next Steps

- Read the full documentation: `MONGODB_SETUP.md`
- Explore the API endpoints
- Customize session management
- Implement user authentication
- Add export/import features

## Getting Help

- Check MongoDB logs: Windows Event Viewer or `/var/log/mongodb/`
- Check Flask console output for errors
- Review browser DevTools Console for JavaScript errors
- Consult `MONGODB_SETUP.md` for detailed documentation

Enjoy your MongoDB-powered chat history! 🚀

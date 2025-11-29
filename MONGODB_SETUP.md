# MongoDB Integration for Articuno.AI

This document explains how to use the MongoDB integration for storing user queries and managing chat history in Articuno.AI.

## Features

- **Session Management**: Automatically creates a unique session ID for each conversation
- **Query Storage**: Stores all user queries and AI responses in MongoDB
- **Chat History**: View and restore previous conversations
- **Session Search**: Search across all messages in your sessions
- **Session Statistics**: Track message counts and activity

## Setup

### 1. Install MongoDB

#### Windows
Download and install MongoDB from: https://www.mongodb.com/try/download/community

#### Linux/Mac
```bash
# Ubuntu/Debian
sudo apt-get install mongodb

# Mac with Homebrew
brew install mongodb-community
```

### 2. Start MongoDB Server

```bash
# Default MongoDB connection
mongod --dbpath /data/db

# Or use the connection string in .env (default: mongodb://127.0.0.1:27017/)
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

The `pymongo` package is already included in requirements.txt.

### 4. Configuration

Add to your `.env` file (optional - uses defaults if not set):

```env
# MongoDB Configuration
MONGODB_URI=mongodb://127.0.0.1:27017/
SECRET_KEY=your-secret-key-here
```

## Usage

### Automatic Session Creation

The system automatically creates a new session when:
- A user starts a conversation for the first time
- A user switches to a different bot
- A user manually creates a new session

Each session gets a unique UUID identifier.

### API Endpoints

#### Create New Session
```http
POST /api/session/new
Content-Type: application/json

{
  "bot": "Articuno.AI"
}
```

Response:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "bot_name": "Articuno.AI",
  "created_at": "2025-11-30T12:00:00"
}
```

#### Get Session History
```http
GET /api/session/history/{session_id}?limit=50
```

Response:
```json
{
  "history": [
    {
      "message_id": "...",
      "session_id": "...",
      "role": "user",
      "message": "What's the weather in London?",
      "bot_name": "Articuno.AI",
      "timestamp": "...",
      "response": "..."
    }
  ]
}
```

#### List User Sessions
```http
GET /api/session/list?limit=10
```

Response:
```json
{
  "sessions": [
    {
      "session_id": "...",
      "bot_name": "Articuno.AI",
      "created_at": "...",
      "last_activity": "...",
      "message_count": 12,
      "status": "active"
    }
  ]
}
```

#### Get Session Statistics
```http
GET /api/session/{session_id}/stats
```

Response:
```json
{
  "session_id": "...",
  "bot_name": "Articuno.AI",
  "created_at": "...",
  "last_activity": "...",
  "total_messages": 24,
  "user_messages": 12,
  "assistant_messages": 12,
  "status": "active"
}
```

#### Delete Session
```http
DELETE /api/session/{session_id}/delete
```

Response:
```json
{
  "message": "Session deleted successfully"
}
```

#### Search Messages
```http
GET /api/search?q=weather&session_id={optional}&limit=20
```

Response:
```json
{
  "results": [
    {
      "message_id": "...",
      "session_id": "...",
      "message": "What's the weather like?",
      "timestamp": "..."
    }
  ]
}
```

## Database Schema

### Collections

#### `sessions` Collection
```javascript
{
  _id: ObjectId("..."),
  session_id: "550e8400-e29b-41d4-a716-446655440000",
  user_id: "anonymous",
  bot_name: "Articuno.AI",
  created_at: ISODate("2025-11-30T12:00:00Z"),
  last_activity: ISODate("2025-11-30T12:30:00Z"),
  message_count: 12,
  status: "active"
}
```

#### `messages` Collection
```javascript
{
  _id: ObjectId("..."),
  message_id: "123e4567-e89b-12d3-a456-426614174000",
  session_id: "550e8400-e29b-41d4-a716-446655440000",
  role: "user",
  message: "What's the weather in London?",
  bot_name: "Articuno.AI",
  timestamp: ISODate("2025-11-30T12:00:00Z"),
  image_data: null,
  response: "The weather in London is..."
}
```

## Frontend Integration

### Session Manager JavaScript

The frontend includes a `SessionManager` class that handles:

```javascript
// Create new session
const sessionId = await sessionManager.createSession('Articuno.AI');

// Load session history
const history = await sessionManager.loadSessionHistory(sessionId);

// List all sessions
const sessions = await sessionManager.listSessions();

// Delete session
await sessionManager.deleteSession(sessionId);

// Search messages
const results = await sessionManager.searchMessages('weather');
```

### UI Features

1. **Recent Sessions Panel**: Shows recent conversations in the sidebar
2. **New Session Button**: Create a new session with one click
3. **Session Restoration**: Click any session to restore its history
4. **Session Deletion**: Delete unwanted sessions
5. **Auto-save**: All messages are automatically saved

## MongoDB Shell Commands

### View Database
```javascript
// Connect to MongoDB
mongo

// Switch to ArticunoAI database
use ArticunoAI

// List all sessions
db.sessions.find().pretty()

// List all messages
db.messages.find().pretty()

// Count sessions
db.sessions.count()

// Count messages
db.messages.count()

// Find specific session
db.sessions.find({session_id: "your-session-id"})

// Find messages by session
db.messages.find({session_id: "your-session-id"}).sort({timestamp: 1})

// Search messages
db.messages.find({message: /weather/i})

// Get session statistics
db.sessions.aggregate([
  {
    $lookup: {
      from: "messages",
      localField: "session_id",
      foreignField: "session_id",
      as: "messages"
    }
  },
  {
    $project: {
      session_id: 1,
      bot_name: 1,
      created_at: 1,
      message_count: { $size: "$messages" }
    }
  }
])
```

### Maintenance Commands
```javascript
// Delete old sessions (older than 30 days)
const thirtyDaysAgo = new Date();
thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
db.sessions.deleteMany({last_activity: {$lt: thirtyDaysAgo}})

// Clean up orphaned messages
const sessionIds = db.sessions.distinct("session_id")
db.messages.deleteMany({session_id: {$nin: sessionIds}})

// Create backup
mongodump --db ArticunoAI --out /backup/articuno-$(date +%Y%m%d)

// Restore backup
mongorestore --db ArticunoAI /backup/articuno-20251130/ArticunoAI
```

## Troubleshooting

### MongoDB Connection Issues

If you see connection errors:

1. **Check MongoDB is running:**
   ```bash
   # Windows
   net start MongoDB
   
   # Linux/Mac
   sudo systemctl status mongod
   ```

2. **Verify connection string:**
   - Default: `mongodb://127.0.0.1:27017/`
   - Check your `.env` file

3. **Check firewall:**
   - Ensure port 27017 is open

### Database Not Saving

1. **Check Python logs** for database errors
2. **Verify pymongo installation:**
   ```bash
   pip show pymongo
   ```
3. **Test connection:**
   ```python
   from pymongo import MongoClient
   client = MongoClient("mongodb://127.0.0.1:27017/")
   print(client.list_database_names())
   ```

### Sessions Not Appearing in UI

1. **Check browser console** for JavaScript errors
2. **Verify session_manager.js** is loaded
3. **Clear browser cache** and reload

## Performance Optimization

### Indexes

The system automatically creates these indexes:
- `messages.session_id`
- `messages.timestamp`
- `sessions.user_id`
- `sessions.created_at`

### Recommended Settings for Production

```javascript
// Increase connection pool size
MONGODB_URI=mongodb://127.0.0.1:27017/?maxPoolSize=50

// Enable replica set for high availability
MONGODB_URI=mongodb://host1,host2,host3/ArticunoAI?replicaSet=rs0
```

## Data Privacy

- Sessions are stored locally by default
- User IDs are set to "anonymous" by default
- Implement authentication to link sessions to real users
- Consider GDPR compliance for production use

## Future Enhancements

- [ ] User authentication and session ownership
- [ ] Export conversations to PDF/JSON
- [ ] Session sharing between users
- [ ] Advanced search with filters
- [ ] Message reactions and favorites
- [ ] Conversation tagging and categorization
- [ ] Analytics dashboard

## Support

For issues or questions:
1. Check MongoDB logs: `/var/log/mongodb/mongod.log`
2. Check Flask logs in console
3. Review browser console for frontend errors

## License

This MongoDB integration is part of Articuno.AI and follows the same license.

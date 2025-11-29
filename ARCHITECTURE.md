# Articuno.AI MongoDB Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND (Browser)                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────┐         ┌─────────────────────────┐    │
│  │  User Interface │         │  Session Manager        │    │
│  │  - Chat Window  │◄───────►│  (session_manager.js)   │    │
│  │  - Sidebar      │         │  - Create session       │    │
│  │  - Input Box    │         │  - Load history         │    │
│  └────────────────┘         │  - List sessions        │    │
│         │                    │  - Delete session       │    │
│         │                    └─────────────────────────┘    │
│         │                              │                     │
└─────────┼──────────────────────────────┼─────────────────────┘
          │                              │
          │ HTTP/JSON                    │ HTTP/JSON
          ▼                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     BACKEND (Flask App)                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐     ┌───────────────┐    ┌─────────────┐ │
│  │  /api/chat   │     │ /api/session  │    │ /api/search │ │
│  │  Endpoints   │     │   Endpoints   │    │  Endpoint   │ │
│  └──────┬───────┘     └───────┬───────┘    └──────┬──────┘ │
│         │                     │                    │        │
│         │                     ▼                    │        │
│         │          ┌──────────────────┐            │        │
│         │          │  DB Manager      │◄───────────┘        │
│         │          │  (db_manager.py) │                     │
│         │          ├──────────────────┤                     │
│         │          │ - create_session │                     │
│         │          │ - save_message   │                     │
│         │          │ - get_history    │                     │
│         │          │ - search_msgs    │                     │
│         │          └────────┬─────────┘                     │
│         │                   │                               │
│         │                   │ pymongo                       │
│         ▼                   ▼                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           AI Agents (Various Bots)                   │  │
│  │  - Articuno.AI  - GPT-4o  - Gemini  - Grok-3  etc.  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────┬────────────────────────────────┘
                              │
                              │ MongoDB Protocol
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      MongoDB Database                        │
├─────────────────────────────────────────────────────────────┤
│                     Database: ArticunoAI                     │
│                                                              │
│  ┌────────────────────┐  ┌────────────────────┐            │
│  │   sessions         │  │   messages         │            │
│  ├────────────────────┤  ├────────────────────┤            │
│  │ - session_id (PK)  │  │ - message_id (PK)  │            │
│  │ - user_id          │  │ - session_id (FK)  │            │
│  │ - bot_name         │  │ - role             │            │
│  │ - created_at       │  │ - message          │            │
│  │ - last_activity    │  │ - bot_name         │            │
│  │ - message_count    │  │ - timestamp        │            │
│  │ - status           │  │ - image_data       │            │
│  └────────────────────┘  │ - response         │            │
│                          └────────────────────┘            │
│                                                              │
│  Indexes:                                                    │
│  - sessions.user_id                                          │
│  - messages.session_id                                       │
│  - messages.timestamp                                        │
│  - messages(session_id, timestamp)                           │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow: Sending a Message

```
1. USER TYPES MESSAGE
   │
   ▼
2. FRONTEND: sendMessage()
   │
   ├─→ Check if session exists
   │   │
   │   ├─→ NO: Create new session
   │   │        POST /api/session/new
   │   │        ↓
   │   │        Get session_id
   │   │
   │   └─→ YES: Use existing session_id
   │
   ▼
3. FRONTEND: POST /api/chat
   {
     "message": "What's the weather?",
     "bot": "Articuno.AI",
     "session_id": "uuid-here"
   }
   │
   ▼
4. BACKEND: chat() endpoint
   │
   ├─→ Route to correct AI agent
   │
   ├─→ Get AI response
   │
   ├─→ Save user message to MongoDB
   │    db.save_message(
   │      session_id,
   │      message,
   │      role="user",
   │      response=ai_response
   │    )
   │
   ├─→ Save AI response to MongoDB
   │    db.save_message(
   │      session_id,
   │      ai_response,
   │      role="assistant"
   │    )
   │
   └─→ Update session.last_activity
        Update session.message_count
   │
   ▼
5. BACKEND: Return response
   {
     "response": "AI response HTML",
     "session_id": "uuid-here"
   }
   │
   ▼
6. FRONTEND: Display response
   │
   └─→ Refresh sessions list in sidebar
```

## Session Lifecycle

```
┌─────────────────────────────────────────────────────┐
│                  SESSION LIFECYCLE                   │
└─────────────────────────────────────────────────────┘

CREATION
   ↓
┌────────────────────┐
│ New session        │
│ - Generate UUID    │ ←─── User starts chatting
│ - Set bot_name     │ ←─── or switches bots
│ - Set user_id      │ ←─── or clicks "New Session"
│ - created_at = now │
│ - message_count=0  │
│ - status = active  │
└─────────┬──────────┘
          │
          ▼
ACTIVE STATE
┌────────────────────┐
│ Session in use     │
│ - Receives msgs    │ ←─── User sends messages
│ - Updates time     │ ←─── AI responds
│ - Increments count │
│ - Shown in sidebar │ ←─── Displayed to user
└─────────┬──────────┘
          │
          ├─→ Click session ──→ RESTORE
          │                    Load all messages
          │                    Display in chat
          │
          ├─→ New bot ────────→ CREATE NEW SESSION
          │                    Switch to new session
          │
          └─→ Delete ─────────→ DELETED
                               Remove from MongoDB
                               Clear from sidebar
```

## Component Interaction

```
┌──────────────┐
│ script.js    │ Main UI logic
└───────┬──────┘
        │
        │ Uses
        │
        ▼
┌────────────────────┐
│ session_manager.js │ Session operations
└───────┬────────────┘
        │
        │ Calls
        │
        ▼
┌──────────────┐
│ Flask API    │ Backend endpoints
└───────┬──────┘
        │
        │ Uses
        │
        ▼
┌──────────────┐
│ db_manager.py│ Database operations
└───────┬──────┘
        │
        │ Connects
        │
        ▼
┌──────────────┐
│ MongoDB      │ Data storage
└──────────────┘
```

## API Endpoints Map

```
/api/session/new
   POST
   ├─→ Create session
   └─→ Return session_id

/api/session/history/<session_id>
   GET
   ├─→ Query messages collection
   └─→ Return message array

/api/session/list
   GET
   ├─→ Query sessions collection
   └─→ Return sessions for user

/api/session/<session_id>/stats
   GET
   ├─→ Aggregate session data
   └─→ Return statistics

/api/session/<session_id>/delete
   DELETE
   ├─→ Delete messages
   ├─→ Delete session
   └─→ Return success

/api/search
   GET
   ├─→ Search messages (regex)
   └─→ Return matching messages

/api/chat
   POST
   ├─→ Process with AI agent
   ├─→ Save to database
   └─→ Return AI response
```

## Database Relationships

```
┌─────────────────┐
│    sessions     │
│ session_id (PK) │◄────────┐
│ user_id         │         │
│ bot_name        │         │ 1:N relationship
│ created_at      │         │ (One session has many messages)
│ last_activity   │         │
│ message_count   │         │
│ status          │         │
└─────────────────┘         │
                            │
                            │
┌─────────────────────────┐ │
│      messages           │ │
│ message_id (PK)         │ │
│ session_id (FK) ────────┘
│ role (user|assistant)   │
│ message (text)          │
│ bot_name                │
│ timestamp               │
│ image_data (optional)   │
│ response (optional)     │
└─────────────────────────┘
```

## Technology Stack

```
┌─────────────────────────────────────┐
│         Frontend Layer              │
├─────────────────────────────────────┤
│ - HTML5                             │
│ - CSS3 (Custom styles)              │
│ - JavaScript (ES6+)                 │
│ - SessionManager class              │
│ - Fetch API                         │
└─────────────────────────────────────┘
              ↕
┌─────────────────────────────────────┐
│         Backend Layer               │
├─────────────────────────────────────┤
│ - Python 3.11+                      │
│ - Flask 2.3.3                       │
│ - Flask Sessions                    │
│ - Various AI Libraries              │
└─────────────────────────────────────┘
              ↕
┌─────────────────────────────────────┐
│       Data Access Layer             │
├─────────────────────────────────────┤
│ - PyMongo 4.6.1                     │
│ - DatabaseManager class             │
│ - Connection pooling                │
└─────────────────────────────────────┘
              ↕
┌─────────────────────────────────────┐
│       Database Layer                │
├─────────────────────────────────────┤
│ - MongoDB 4.4+                      │
│ - Database: ArticunoAI              │
│ - Collections: sessions, messages   │
│ - Indexes for performance           │
└─────────────────────────────────────┘
```

## Deployment Architecture

```
Development:
┌─────────────┐
│ Flask Dev   │
│ Server      │ localhost:5000
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ MongoDB     │ localhost:27017
└─────────────┘

Production (Example):
┌─────────────┐     ┌─────────────┐
│ Load        │────►│ Gunicorn    │
│ Balancer    │     │ Workers     │
│ (Nginx)     │     │ (Flask)     │
└─────────────┘     └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ MongoDB     │
                    │ Replica Set │
                    │ (Cluster)   │
                    └─────────────┘
```

This architecture provides a solid foundation for your AI chatbot with persistent storage!

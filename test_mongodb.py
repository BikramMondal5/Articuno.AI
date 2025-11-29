"""
Test script for MongoDB integration
Run this to verify your MongoDB setup is working correctly
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from database.db_manager import get_db_manager
    print("✓ Successfully imported database module")
except ImportError as e:
    print(f"✗ Failed to import database module: {e}")
    print("  Make sure pymongo is installed: pip install pymongo==4.6.1")
    sys.exit(1)

def test_connection():
    """Test MongoDB connection"""
    print("\n--- Testing MongoDB Connection ---")
    try:
        db = get_db_manager("mongodb://127.0.0.1:27017/")
        
        # Try to access the database
        db.client.server_info()
        print("✓ Successfully connected to MongoDB")
        return db
    except Exception as e:
        print(f"✗ Failed to connect to MongoDB: {e}")
        print("  Make sure MongoDB is running:")
        print("    Windows: net start MongoDB")
        print("    Linux: sudo systemctl start mongod")
        return None

def test_create_session(db):
    """Test session creation"""
    print("\n--- Testing Session Creation ---")
    try:
        session_id = db.create_session(user_id="test_user", bot_name="Test Bot")
        print(f"✓ Created session: {session_id}")
        return session_id
    except Exception as e:
        print(f"✗ Failed to create session: {e}")
        return None

def test_save_message(db, session_id):
    """Test message saving"""
    print("\n--- Testing Message Saving ---")
    try:
        message_id = db.save_message(
            session_id=session_id,
            message="Test message from test script",
            role="user",
            bot_name="Test Bot",
            response="Test response"
        )
        print(f"✓ Saved message: {message_id}")
        
        # Save assistant response
        message_id2 = db.save_message(
            session_id=session_id,
            message="Test response",
            role="assistant",
            bot_name="Test Bot"
        )
        print(f"✓ Saved assistant message: {message_id2}")
        return True
    except Exception as e:
        print(f"✗ Failed to save message: {e}")
        return False

def test_get_history(db, session_id):
    """Test retrieving session history"""
    print("\n--- Testing Session History Retrieval ---")
    try:
        history = db.get_session_history(session_id)
        print(f"✓ Retrieved {len(history)} messages")
        for msg in history:
            print(f"  - [{msg['role']}] {msg['message'][:50]}...")
        return True
    except Exception as e:
        print(f"✗ Failed to retrieve history: {e}")
        return False

def test_list_sessions(db):
    """Test listing sessions"""
    print("\n--- Testing Session Listing ---")
    try:
        sessions = db.get_user_sessions(user_id="test_user")
        print(f"✓ Found {len(sessions)} session(s) for test_user")
        for sess in sessions:
            print(f"  - {sess['bot_name']}: {sess['message_count']} messages")
        return True
    except Exception as e:
        print(f"✗ Failed to list sessions: {e}")
        return False

def test_session_stats(db, session_id):
    """Test session statistics"""
    print("\n--- Testing Session Statistics ---")
    try:
        stats = db.get_session_stats(session_id)
        print("✓ Session statistics:")
        print(f"  - Bot: {stats.get('bot_name')}")
        print(f"  - Total messages: {stats.get('total_messages')}")
        print(f"  - User messages: {stats.get('user_messages')}")
        print(f"  - Assistant messages: {stats.get('assistant_messages')}")
        print(f"  - Status: {stats.get('status')}")
        return True
    except Exception as e:
        print(f"✗ Failed to get session stats: {e}")
        return False

def test_search(db):
    """Test message search"""
    print("\n--- Testing Message Search ---")
    try:
        results = db.search_messages("test", limit=5)
        print(f"✓ Found {len(results)} message(s) matching 'test'")
        for msg in results[:3]:  # Show first 3
            print(f"  - {msg['message'][:60]}...")
        return True
    except Exception as e:
        print(f"✗ Failed to search messages: {e}")
        return False

def cleanup(db, session_id):
    """Clean up test data"""
    print("\n--- Cleaning Up Test Data ---")
    try:
        db.delete_session(session_id)
        print("✓ Deleted test session")
        return True
    except Exception as e:
        print(f"✗ Failed to cleanup: {e}")
        return False

def main():
    print("=" * 60)
    print("MongoDB Integration Test Script")
    print("=" * 60)
    
    # Test connection
    db = test_connection()
    if not db:
        print("\n❌ Cannot proceed without MongoDB connection")
        return False
    
    # Run tests
    session_id = test_create_session(db)
    if not session_id:
        print("\n❌ Tests failed")
        return False
    
    test_save_message(db, session_id)
    test_get_history(db, session_id)
    test_list_sessions(db)
    test_session_stats(db, session_id)
    test_search(db)
    
    # Ask before cleanup
    print("\n" + "=" * 60)
    cleanup_choice = input("Delete test session? (y/n): ").lower()
    if cleanup_choice == 'y':
        cleanup(db, session_id)
    else:
        print(f"Test session kept: {session_id}")
    
    print("\n" + "=" * 60)
    print("✅ All tests completed successfully!")
    print("=" * 60)
    print("\nYour MongoDB integration is working correctly!")
    print("You can now use Articuno.AI with persistent chat history.")
    print("\nNext steps:")
    print("  1. Start your Flask app: python app.py")
    print("  2. Open http://localhost:5000 in your browser")
    print("  3. Start chatting and watch your sessions appear in the sidebar")
    print("\nFor more information, see MONGODB_SETUP.md")
    
    db.close()
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

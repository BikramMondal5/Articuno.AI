"""
Clear all existing sessions from MongoDB
Use this to start fresh with the new history feature
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from database.db_manager import get_db_manager
    print("✓ Successfully imported database module")
except ImportError as e:
    print(f"✗ Failed to import database module: {e}")
    sys.exit(1)

def clear_all_sessions():
    """Clear all sessions and messages from the database"""
    print("\n--- Clearing All Sessions ---")
    
    try:
        db = get_db_manager("mongodb://127.0.0.1:27017/")
        
        # Count before deletion
        session_count = db.sessions.count_documents({})
        message_count = db.messages.count_documents({})
        
        print(f"Found {session_count} session(s) and {message_count} message(s)")
        
        if session_count == 0:
            print("No sessions to delete. Database is already empty.")
            db.close()
            return
        
        # Confirm deletion
        confirm = input(f"\nAre you sure you want to delete all {session_count} sessions? (yes/no): ")
        
        if confirm.lower() != 'yes':
            print("Operation cancelled.")
            db.close()
            return
        
        # Delete all messages
        result_messages = db.messages.delete_many({})
        print(f"✓ Deleted {result_messages.deleted_count} messages")
        
        # Delete all sessions
        result_sessions = db.sessions.delete_many({})
        print(f"✓ Deleted {result_sessions.deleted_count} sessions")
        
        print("\n✅ All sessions cleared successfully!")
        print("You can now start fresh with the new 'History' feature.")
        print("New sessions will show the last user question as the title.")
        
        db.close()
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("Clear MongoDB Sessions")
    print("=" * 60)
    clear_all_sessions()

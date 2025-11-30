"""
MongoDB Database Manager for Articuno.AI
Handles user queries, chat history, and session management
"""

from pymongo import MongoClient
from datetime import datetime
import uuid
from typing import Optional, List, Dict, Any

class DatabaseManager:
    """Manages MongoDB connections and operations for chat history"""
    
    def __init__(self, connection_string: str = "mongodb://127.0.0.1:27017/"):
        """
        Initialize the database connection
        
        Args:
            connection_string: MongoDB connection string
        """
        self.client = MongoClient(connection_string)
        self.db = self.client['ArticunoAI']
        
        # Collections
        self.sessions = self.db['sessions']
        self.messages = self.db['messages']
        self.users = self.db['users']
        
        # Create indexes for better performance
        self._create_indexes()
    
    def _create_indexes(self):
        """Create database indexes for optimal performance"""
        # Index on session_id for fast lookups
        self.messages.create_index('session_id')
        
        # Index on timestamp for sorting
        self.messages.create_index('timestamp')
        
        # Compound index for session queries
        self.messages.create_index([('session_id', 1), ('timestamp', -1)])
        
        # Index on user_id for user-specific queries
        self.sessions.create_index('user_id')
        self.sessions.create_index('created_at')
    
    def create_session(self, user_id: Optional[str] = None, bot_name: str = "Articuno.AI") -> str:
        """
        Create a new chat session
        
        Args:
            user_id: Optional user identifier
            bot_name: Name of the bot being used
            
        Returns:
            session_id: Unique session identifier
        """
        session_id = str(uuid.uuid4())
        
        session_data = {
            'session_id': session_id,
            'user_id': user_id or 'anonymous',
            'bot_name': bot_name,
            'created_at': datetime.utcnow(),
            'last_activity': datetime.utcnow(),
            'message_count': 0,
            'status': 'active',
            'last_user_query': None  # Will be updated when first message is sent
        }
        
        self.sessions.insert_one(session_data)
        return session_id
    
    def save_message(self, 
                    session_id: str, 
                    message: str, 
                    role: str = 'user',
                    bot_name: str = "Articuno.AI",
                    image_data: Optional[Dict] = None,
                    response: Optional[str] = None) -> str:
        """
        Save a message to the database
        
        Args:
            session_id: Session identifier
            message: The message text
            role: 'user' or 'assistant'
            bot_name: Name of the bot
            image_data: Optional image data dictionary
            response: Optional AI response (if role is 'user')
            
        Returns:
            message_id: Unique message identifier
        """
        message_id = str(uuid.uuid4())
        
        message_data = {
            'message_id': message_id,
            'session_id': session_id,
            'role': role,
            'message': message,
            'bot_name': bot_name,
            'timestamp': datetime.utcnow(),
            'image_data': image_data,
            'response': response
        }
        
        self.messages.insert_one(message_data)
        
        # Update session activity and last_user_query if this is a user message
        update_data = {
            '$set': {'last_activity': datetime.utcnow()},
            '$inc': {'message_count': 1}
        }
        
        # Update last_user_query if this is a user message
        if role == 'user':
            update_data['$set']['last_user_query'] = message
        
        self.sessions.update_one(
            {'session_id': session_id},
            update_data
        )
        
        return message_id
    
    def get_session_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieve chat history for a session
        
        Args:
            session_id: Session identifier
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of message dictionaries
        """
        messages = self.messages.find(
            {'session_id': session_id}
        ).sort('timestamp', 1).limit(limit)
        
        return list(messages)
    
    def get_user_sessions(self, user_id: str = 'anonymous', limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get all sessions for a user
        
        Args:
            user_id: User identifier
            limit: Maximum number of sessions to retrieve
            
        Returns:
            List of session dictionaries
        """
        sessions = self.sessions.find(
            {'user_id': user_id}
        ).sort('last_activity', -1).limit(limit)
        
        return list(sessions)
    
    def get_recent_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent sessions across all users
        
        Args:
            limit: Maximum number of sessions to retrieve
            
        Returns:
            List of session dictionaries
        """
        sessions = self.sessions.find().sort('last_activity', -1).limit(limit)
        return list(sessions)
    
    def end_session(self, session_id: str):
        """
        Mark a session as ended
        
        Args:
            session_id: Session identifier
        """
        self.sessions.update_one(
            {'session_id': session_id},
            {
                '$set': {
                    'status': 'ended',
                    'ended_at': datetime.utcnow()
                }
            }
        )
    
    def delete_session(self, session_id: str):
        """
        Delete a session and all its messages
        
        Args:
            session_id: Session identifier
        """
        self.messages.delete_many({'session_id': session_id})
        self.sessions.delete_one({'session_id': session_id})
    
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """
        Get statistics for a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary with session statistics
        """
        session = self.sessions.find_one({'session_id': session_id})
        if not session:
            return {}
        
        message_count = self.messages.count_documents({'session_id': session_id})
        user_messages = self.messages.count_documents({'session_id': session_id, 'role': 'user'})
        assistant_messages = self.messages.count_documents({'session_id': session_id, 'role': 'assistant'})
        
        return {
            'session_id': session_id,
            'bot_name': session.get('bot_name'),
            'created_at': session.get('created_at'),
            'last_activity': session.get('last_activity'),
            'total_messages': message_count,
            'user_messages': user_messages,
            'assistant_messages': assistant_messages,
            'status': session.get('status')
        }
    
    def search_messages(self, query: str, session_id: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search for messages containing specific text
        
        Args:
            query: Search query
            session_id: Optional session to search within
            limit: Maximum number of results
            
        Returns:
            List of matching messages
        """
        search_filter = {'message': {'$regex': query, '$options': 'i'}}
        
        if session_id:
            search_filter['session_id'] = session_id
        
        messages = self.messages.find(search_filter).sort('timestamp', -1).limit(limit)
        return list(messages)
    
    def close(self):
        """Close the database connection"""
        if self.client:
            self.client.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Singleton instance
_db_instance = None

def get_db_manager(connection_string: str = "mongodb://127.0.0.1:27017/") -> DatabaseManager:
    """
    Get or create a DatabaseManager singleton instance
    
    Args:
        connection_string: MongoDB connection string
        
    Returns:
        DatabaseManager instance
    """
    global _db_instance
    
    if _db_instance is None:
        _db_instance = DatabaseManager(connection_string)
    
    return _db_instance

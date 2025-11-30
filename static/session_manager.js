/**
 * Session Manager for Articuno.AI
 * Handles session creation, history loading, and session management
 */

class SessionManager {
    constructor() {
        this.currentSessionId = null;
        this.currentBot = 'Articuno.AI';
    }

    /**
     * Create a new chat session
     * @param {string} botName - Name of the bot for this session
     * @returns {Promise<string>} - Session ID
     */
    async createSession(botName = 'Articuno.AI') {
        try {
            const response = await fetch('/api/session/new', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ bot: botName })
            });

            const data = await response.json();
            
            if (data.error) {
                console.error('Error creating session:', data.error);
                return null;
            }

            this.currentSessionId = data.session_id;
            this.currentBot = botName;
            
            console.log('New session created:', this.currentSessionId);
            
            // Store in localStorage
            localStorage.setItem('current_session_id', this.currentSessionId);
            localStorage.setItem('current_bot', this.currentBot);
            
            return this.currentSessionId;
        } catch (error) {
            console.error('Error creating session:', error);
            return null;
        }
    }

    /**
     * Get the current session ID
     * @returns {string|null} - Current session ID
     */
    getCurrentSessionId() {
        if (!this.currentSessionId) {
            // Try to restore from localStorage
            this.currentSessionId = localStorage.getItem('current_session_id');
        }
        return this.currentSessionId;
    }

    /**
     * Load session history from server
     * @param {string} sessionId - Session ID to load
     * @param {number} limit - Maximum number of messages to load
     * @returns {Promise<Array>} - Array of messages
     */
    async loadSessionHistory(sessionId, limit = 50) {
        try {
            const response = await fetch(`/api/session/history/${sessionId}?limit=${limit}`);
            const data = await response.json();
            
            if (data.error) {
                console.error('Error loading history:', data.error);
                return [];
            }

            return data.history || [];
        } catch (error) {
            console.error('Error loading session history:', error);
            return [];
        }
    }

    /**
     * Get list of user's recent sessions
     * @param {number} limit - Maximum number of sessions to retrieve
     * @returns {Promise<Array>} - Array of session objects
     */
    async listSessions(limit = 10) {
        try {
            const response = await fetch(`/api/session/list?limit=${limit}`);
            const data = await response.json();
            
            if (data.error) {
                console.error('Error listing sessions:', data.error);
                return [];
            }

            return data.sessions || [];
        } catch (error) {
            console.error('Error listing sessions:', error);
            return [];
        }
    }

    /**
     * Get statistics for a session
     * @param {string} sessionId - Session ID
     * @returns {Promise<Object>} - Session statistics
     */
    async getSessionStats(sessionId) {
        try {
            const response = await fetch(`/api/session/${sessionId}/stats`);
            const data = await response.json();
            
            if (data.error) {
                console.error('Error getting stats:', data.error);
                return {};
            }

            return data;
        } catch (error) {
            console.error('Error getting session stats:', error);
            return {};
        }
    }

    /**
     * Delete a session
     * @param {string} sessionId - Session ID to delete
     * @returns {Promise<boolean>} - Success status
     */
    async deleteSession(sessionId) {
        try {
            const response = await fetch(`/api/session/${sessionId}/delete`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            
            if (data.error) {
                console.error('Error deleting session:', data.error);
                return false;
            }

            // Clear current session if it's the one being deleted
            if (this.currentSessionId === sessionId) {
                this.currentSessionId = null;
                localStorage.removeItem('current_session_id');
            }

            return true;
        } catch (error) {
            console.error('Error deleting session:', error);
            return false;
        }
    }

    /**
     * Search messages across sessions
     * @param {string} query - Search query
     * @param {string|null} sessionId - Optional session ID to limit search
     * @param {number} limit - Maximum number of results
     * @returns {Promise<Array>} - Array of matching messages
     */
    async searchMessages(query, sessionId = null, limit = 20) {
        try {
            let url = `/api/search?q=${encodeURIComponent(query)}&limit=${limit}`;
            if (sessionId) {
                url += `&session_id=${sessionId}`;
            }

            const response = await fetch(url);
            const data = await response.json();
            
            if (data.error) {
                console.error('Error searching messages:', data.error);
                return [];
            }

            return data.results || [];
        } catch (error) {
            console.error('Error searching messages:', error);
            return [];
        }
    }

    /**
     * Start a new session when switching bots
     * @param {string} botName - Name of the new bot
     */
    async switchBot(botName) {
        console.log(`Switching to ${botName}, creating new session...`);
        await this.createSession(botName);
    }

    /**
     * Display session history in the chat interface
     * @param {string} sessionId - Session ID to display
     * @param {HTMLElement} chatHistoryElement - Chat history container element
     */
    async displaySessionHistory(sessionId, chatHistoryElement) {
        try {
            const history = await this.loadSessionHistory(sessionId);
            
            // Clear current chat history
            chatHistoryElement.innerHTML = '';
            
            // Display each message
            history.forEach(msg => {
                if (msg.role === 'user') {
                    // Display user message
                    addMessageToHistory(msg.message, true, msg.image_data, chatHistoryElement);
                    
                    // Display AI response if it exists
                    if (msg.response) {
                        addAIMessageToHistory(msg.response, chatHistoryElement);
                    }
                } else if (msg.role === 'assistant') {
                    // Legacy support for old assistant messages (if any exist)
                    addAIMessageToHistory(msg.message, chatHistoryElement);
                }
            });
            
            // Scroll to bottom
            chatHistoryElement.scrollTop = chatHistoryElement.scrollHeight;
            
            return history.length;
        } catch (error) {
            console.error('Error displaying session history:', error);
            return 0;
        }
    }

    /**
     * Render sessions list in the sidebar
     * @param {HTMLElement} containerElement - Container to render sessions in
     */
    async renderSessionsList(containerElement) {
        try {
            const sessions = await this.listSessions();
            
            if (sessions.length === 0) {
                containerElement.innerHTML = '<div class="no-sessions">No history yet</div>';
                return;
            }

            containerElement.innerHTML = '';
            
            sessions.forEach(session => {
                const sessionItem = document.createElement('div');
                sessionItem.className = 'session-item';
                
                const sessionInfo = document.createElement('div');
                sessionInfo.className = 'session-info';
                
                const sessionTitle = document.createElement('div');
                sessionTitle.className = 'session-title';
                
                // Use last_user_query as title, truncate if too long
                let title = session.last_user_query || 'New conversation';
                if (title.length > 60) {
                    title = title.substring(0, 57) + '...';
                }
                sessionTitle.textContent = title;
                sessionTitle.title = session.last_user_query || 'New conversation'; // Full text on hover
                
                const sessionMeta = document.createElement('div');
                sessionMeta.className = 'session-meta';
                
                const messageCount = session.message_count || 0;
                const lastActivity = new Date(session.last_activity.$date || session.last_activity);
                const timeAgo = this.getTimeAgo(lastActivity);
                
                sessionMeta.textContent = `${messageCount} messages • ${timeAgo}`;
                
                sessionInfo.appendChild(sessionTitle);
                sessionInfo.appendChild(sessionMeta);
                
                // Delete button
                const deleteBtn = document.createElement('button');
                deleteBtn.className = 'session-delete-btn';
                deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
                deleteBtn.onclick = async (e) => {
                    e.stopPropagation();
                    if (confirm('Delete this conversation?')) {
                        await this.deleteSession(session.session_id);
                        this.renderSessionsList(containerElement);
                    }
                };
                
                sessionItem.appendChild(sessionInfo);
                sessionItem.appendChild(deleteBtn);
                
                // Click to load session
                sessionItem.onclick = () => {
                    this.currentSessionId = session.session_id;
                    this.currentBot = session.bot_name;
                    localStorage.setItem('current_session_id', this.currentSessionId);
                    localStorage.setItem('current_bot', this.currentBot);
                    
                    // Map bot names to their avatar IDs
                    const botAvatarMap = {
                        'Articuno.AI': 'Articuno-avatar',
                        'Wikipedia DeepSearch': 'wikipedia-avatar',
                        'Codestral 2501': 'codestral-2501-avatar',
                        'DeepSeek R1': 'DeepSeek-avatar',
                        'DeepSeek V3': 'DeepSeek-V3-avatar',
                        'Gemini 2.0 Flash': 'gemini-avatar',
                        'Gemini 2.5 Flash': 'gemini-25-avatar',
                        'GPT-4o': 'gpt-4o-avatar',
                        'GPT-4o-mini': 'gpt-4o-mini-avatar',
                        'Grok-3': 'grok3-avatar',
                        'Grok-3 Mini': 'grok3-mini-avatar',
                        'Ministral 3B': 'ministral-3b-avatar'
                    };
                    
                    const avatarId = botAvatarMap[session.bot_name] || 'Articuno-avatar';
                    
                    // Update the assistantProfile to match the loaded session's bot
                    if (typeof assistantProfile !== 'undefined') {
                        assistantProfile.name = session.bot_name;
                        assistantProfile.avatar = avatarId;
                        
                        // Update the UI to reflect the loaded session's bot
                        const chatInputHeader = document.querySelector('.chat-input-header');
                        if (chatInputHeader) {
                            const headerAvatar = chatInputHeader.querySelector('.bot-avatar');
                            const headerName = chatInputHeader.querySelector('.models-name');
                            
                            if (headerAvatar) {
                                headerAvatar.id = avatarId;
                            }
                            if (headerName) {
                                headerName.textContent = session.bot_name;
                            }
                        }
                        
                        // Update chatbot interface header with both name and avatar
                        const chatbotName = document.querySelector('.chatbot-info h2');
                        if (chatbotName) {
                            chatbotName.textContent = session.bot_name;
                        }
                        
                        const chatbotAvatarDisplay = document.querySelector('.chatbot-header .chatbot-avatar');
                        if (chatbotAvatarDisplay) {
                            chatbotAvatarDisplay.id = avatarId;
                        }
                    }
                    
                    // Show chat interface if not already visible
                    const mainGrid = document.querySelector('.main-grid-layout');
                    const chatbotShowcase = document.getElementById('chatbot-showcase');
                    const chatbotInterface = document.getElementById('chatbot-interface');
                    
                    if (mainGrid) mainGrid.style.display = 'none';
                    if (chatbotShowcase) chatbotShowcase.style.display = 'none';
                    if (chatbotInterface) chatbotInterface.style.display = 'flex';
                    
                    // Show the bottom bar when loading a session
                    const bottomBar = document.querySelector('.bottom-bar');
                    if (bottomBar) {
                        bottomBar.style.display = 'block';
                    }
                    
                    // Display the session history
                    const chatHistory = document.getElementById('chatbot-chat-history');
                    if (chatHistory) {
                        this.displaySessionHistory(session.session_id, chatHistory);
                    }
                    
                    // Highlight active session
                    document.querySelectorAll('.session-item').forEach(item => {
                        item.classList.remove('active');
                    });
                    sessionItem.classList.add('active');
                };
                
                // Highlight current session
                if (session.session_id === this.currentSessionId) {
                    sessionItem.classList.add('active');
                }
                
                containerElement.appendChild(sessionItem);
            });
        } catch (error) {
            console.error('Error rendering sessions list:', error);
        }
    }

    /**
     * Get human-readable time ago string
     * @param {Date} date - Date to compare
     * @returns {string} - Time ago string
     */
    getTimeAgo(date) {
        const seconds = Math.floor((new Date() - date) / 1000);
        
        if (seconds < 60) return 'just now';
        
        const minutes = Math.floor(seconds / 60);
        if (minutes < 60) return `${minutes}m ago`;
        
        const hours = Math.floor(minutes / 60);
        if (hours < 24) return `${hours}h ago`;
        
        const days = Math.floor(hours / 24);
        if (days < 7) return `${days}d ago`;
        
        const weeks = Math.floor(days / 7);
        if (weeks < 4) return `${weeks}w ago`;
        
        const months = Math.floor(days / 30);
        return `${months}mo ago`;
    }
}

// Create global session manager instance
const sessionManager = new SessionManager();

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SessionManager;
}

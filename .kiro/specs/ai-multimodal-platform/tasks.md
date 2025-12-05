# Implementation Plan

# Implementation Plan

- [x] 1. Set up project structure and core infrastructure





  - Create Flask project with Python virtual environment
  - Set up testing framework (pytest and Hypothesis for property-based testing)
  - Create directory structure: templates/, static/css/, static/js/, services/, adapters/, utils/, models/
  - Install dependencies: Flask, cryptography, requests, pytest, hypothesis
  - Configure Flask app with secret key and session management
  - _Requirements: 5.1, 5.2, 5.5_

- [x] 2. Implement secure storage and authentication system




  - [x] 2.1 Create StorageManager for Flask session operations


    - Implement set, get, remove, and clear methods using Flask sessions
    - Add error handling for session storage issues
    - _Requirements: 2.1, 2.2_
  
  - [x] 2.2 Implement encryption utilities using Python cryptography library


    - Create encrypt/decrypt functions for GitHub PAT using Fernet
    - Generate and manage encryption keys
    - Handle secure key storage
    - _Requirements: 1.4, 2.5_
  
  - [ ]* 2.3 Write property test for encryption round-trip
    - **Property 1: PAT Storage Encryption**
    - **Validates: Requirements 1.4, 2.5**
  
  - [x] 2.4 Create AuthenticationManager service (Python class)


    - Implement PAT format validation (GitHub token patterns)
    - Implement store_pat, retrieve_pat, remove_pat methods
    - Manage authentication state (is_authenticated)
    - _Requirements: 1.1, 1.2, 1.3, 6.2, 6.3, 6.5_
  
  - [ ]* 2.5 Write property tests for authentication operations
    - **Property 2: Authentication State Consistency**
    - **Property 7: Invalid PAT Rejection**
    - **Property 8: Credential Update Atomicity**
    - **Validates: Requirements 1.1, 1.2, 1.3, 6.2, 6.4**

- [x] 3. Build AI model integration layer





  - [x] 3.1 Create base ModelAdapter abstract class (Python)


    - Define common interface for all model adapters
    - Implement shared error handling and retry logic
    - Add request/response normalization utilities
    - _Requirements: 4.1, 4.3_
  
  - [x] 3.2 Implement chat model adapters (Python classes)


    - Create GPT4oAdapter for OpenAI API
    - Create DeepSeekAdapter for DeepSeek API
    - Create GeminiAdapter for Google AI API
    - Create MistralAdapter for Mistral AI API
    - Each adapter handles authentication with GitHub PAT
    - Implement both standard and streaming response handling
    - _Requirements: 4.1, 4.5_
  
  - [x] 3.3 Create ModelRouter service (Python class)


    - Implement model selection and tracking (select_model, get_active_model)
    - Route requests to appropriate adapter based on active model
    - Handle streaming and non-streaming responses
    - _Requirements: 3.2, 3.3, 4.1_
  
  - [ ]* 3.4 Write property tests for model routing
    - **Property 9: Direct API Communication**
    - **Validates: Requirements 5.3, 5.4**

- [x] 4. Implement Python/LangChain integration for agent models





  - [x] 4.1 Set up LangChain integration in Flask


    - Install LangChain dependencies
    - Configure environment variables for API keys (Weather API, etc.)
    - Create Flask routes for agent execution
    - _Requirements: 9.3_
  
  - [x] 4.2 Create Tool Registry and base tool implementations (Python)


    - Implement ToolRegistry service as Python class
    - Create Tool base class and implementations
    - Register tools for each agent model
    - _Requirements: 9.3_
  
  - [x] 4.3 Implement Articuno.AI weather agent (Python)


    - Create ArticunoAdapter extending AgentAdapter
    - Implement weather tool using OpenWeatherMap or similar API
    - Add location parsing and validation
    - Format weather data into natural language responses
    - Handle weather API errors and invalid locations
    - _Requirements: 9.1, 10.1, 10.2, 10.3, 10.4, 10.5_
  
  - [x] 4.4 Implement Bikram.AI coding agent (Python)


    - Create BikramAdapter extending AgentAdapter
    - Implement code validation tool
    - Implement code explanation tool
    - Add syntax checking and linting capabilities
    - Format coding assistance into helpful responses
    - _Requirements: 9.2, 11.1, 11.2, 11.3, 11.4, 11.5_
  
  - [ ]* 4.5 Write property tests for agent tool calling
    - **Property 11: Tool Call Execution**
    - **Property 12: Agent Tool Isolation**
    - **Property 13: Weather Data Freshness**
    - **Property 14: Tool Call Status Visibility**
    - **Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5, 10.2**

- [x] 5. Implement conversation management




  - [x] 5.1 Create ConversationManager service (Python class)


    - Implement add_message, get_history, clear_history methods
    - Maintain separate conversation state per model
    - Persist conversations to Flask session via StorageManager
    - Implement export_conversation functionality
    - _Requirements: 3.4, 4.4_
  
  - [ ]* 5.2 Write property tests for conversation isolation
    - **Property 4: Model Selection Persistence**
    - **Property 5: Conversation Context Isolation**
    - **Validates: Requirements 3.4, 4.4**

- [x] 6. Build authentication UI templates and routes





  - [x] 6.1 Create login.html template and Flask route


    - Build PAT input form with validation feedback (HTML/CSS)
    - Display GitHub PAT generation instructions
    - Show estimated time (30 seconds) and free cost messaging
    - Include links to GitHub documentation
    - Handle authentication errors with clear messaging
    - Create /login POST route in Flask
    - _Requirements: 1.1, 1.3, 7.3, 7.4, 8.1, 8.2, 8.3, 8.4, 8.5_
  
  - [x] 6.2 Create settings.html template for credential management


    - Display masked PAT view
    - Implement PAT update functionality with validation
    - Add logout button with confirmation
    - Create /settings and /logout routes in Flask
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 7. Build main chat interface




  - [x] 7.1 Create chat.html template with model selector


    - Display all available models (GPT-4o, DeepSeek, Gemini, Mistral, Articuno.AI, Bikram.AI)
    - Indicate model category (chat vs agent) using HTML/CSS
    - Highlight currently active model
    - Handle model switching with JavaScript
    - Create /select_model route in Flask
    - _Requirements: 3.1, 3.2, 3.5_
  
  - [x] 7.2 Build chat interface in chat.html


    - Build message input area with send button (HTML/CSS)
    - Display conversation history with user/assistant messages
    - Show loading indicators during API calls (JavaScript)
    - Display typing indicators for streaming responses
    - Handle empty input validation with JavaScript
    - Create /send_message route in Flask
    - _Requirements: 4.1, 4.2, 7.1, 7.2, 7.5_
  
  - [x] 7.3 Create message display section in chat.html


    - Render messages with timestamps (HTML/CSS)
    - Support markdown formatting in responses (JavaScript library)
    - Auto-scroll to latest message (JavaScript)
    - _Requirements: 4.2_

  - [x] 7.4 Add tool call display to chat.html


    - Show tool execution status (pending, success, error)
    - Display tool parameters and results
    - Format tool calls in conversation history
    - _Requirements: 9.4_


- [x] 8. Implement error handling and user feedback




  - [x] 8.1 Create error display in templates


    - Show user-friendly error messages (HTML/CSS)
    - Provide actionable guidance for different error types
    - Handle authentication, network, and API errors
    - Use Flask flash messages for error display
    - _Requirements: 1.3, 4.3, 7.3_
  
  - [ ]* 8.2 Write property test for error messages
    - **Property 10: Error Message Clarity**
    - **Validates: Requirements 7.3**
  
  - [x] 8.3 Add comprehensive error handling across all Python services


    - Handle network failures with retry suggestions
    - Handle rate limiting with wait time display
    - Handle expired/invalid PAT with re-authentication prompts
    - Handle storage failures with troubleshooting guidance
    - _Requirements: 4.3, 7.3_

- [x] 9. Wire up application state and routing





  - [x] 9.1 Create Flask application state management


    - Manage authentication state in Flask session
    - Track active model selection in session
    - Coordinate between services and routes
    - _Requirements: 3.2, 3.4_
  
  - [x] 9.2 Implement main Flask app.py


    - Route between login and chat pages based on auth state
    - Initialize services on app startup
    - Check for existing authentication on request
    - Handle session restoration from Flask session
    - _Requirements: 2.2, 5.1, 5.2_
  
  - [x] 9.3 Connect all routes and services


    - Wire AuthenticationManager to login routes
    - Connect ModelRouter to chat routes
    - Link ConversationManager to message routes
    - Integrate StorageManager across all routes
    - _Requirements: All_

- [x] 10. Add security and privacy features

  - [x] 10.1 Implement secure credential handling in Flask

    - Ensure PAT never appears in Flask logs
    - Prevent PAT from being logged in network requests
    - Clear sensitive data from session on logout
    - Configure secure session cookies
    - _Requirements: 1.5, 2.4, 6.3_
  
  - [x] 10.2 Add HTTPS-only enforcement and security headers


    - Configure Flask to only make HTTPS requests
    - Add Content Security Policy headers
    - Set secure cookie flags (httponly, secure, samesite)
    - _Requirements: 5.3_

  - [ ]* 10.3 Write property test for no server transmission
    - **Property 3: No Server Transmission**
    - **Validates: Requirements 1.5, 2.4**

- [x] 11. Set up URL summarizer agent module

  - Create `agent/url_summarizer.py` file with basic structure
  - Import required dependencies (requests, beautifulsoup4, azure.ai.inference, markdown, re)
  - Set up Azure AI Inference client configuration using GITHUB_TOKEN from environment
  - Add logging for debugging and monitoring
  - _Requirements: 5.1, 5.2, 7.1, 7.2, 7.3_

- [ ]* 11.1 Write property test for URL validation
  - **Property 1: URL Validation Accepts Valid URLs**
  - **Validates: Requirements 1.1**

- [ ]* 11.2 Write property test for invalid URL rejection
  - **Property 2: URL Validation Rejects Invalid Formats**
  - **Validates: Requirements 1.3**

- [x] 12. Implement URL validation and content extraction

  - Create `validate_url()` function to check URL format using regex
  - Create `extract_content_from_url()` function to fetch and parse HTML
  - Implement HTTP request with proper timeout, headers, and error handling
  - Use BeautifulSoup4 to parse HTML and extract main content
  - Filter out unwanted elements (nav, footer, aside, script, style, ads)
  - Handle network errors, timeouts, and HTTP error codes gracefully
  - _Requirements: 1.1, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ]* 12.1 Write property test for content fetching
  - **Property 3: Content Fetching Success**
  - **Validates: Requirements 2.1**

- [ ]* 12.2 Write property test for main content extraction
  - **Property 4: Main Content Extraction**
  - **Validates: Requirements 2.2, 2.3**

- [ ]* 12.3 Write property test for character encoding
  - **Property 5: Character Encoding Preservation**
  - **Validates: Requirements 2.5**

- [x] 13. Implement AI summarization functionality

  - Create `summarize_content()` function using Azure AI Inference
  - Design system prompt for web content summarization
  - Configure AI model parameters (temperature, max_tokens, etc.)
  - Handle long content by truncating to token limits
  - Implement error handling for API failures and rate limiting
  - Convert AI response from markdown to HTML
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ]* 13.1 Write property test for summarization output
  - **Property 6: Summarization Produces Output**
  - **Validates: Requirements 3.1, 3.2**

- [ ]* 13.2 Write property test for markdown formatting
  - **Property 7: Summary Markdown Formatting**
  - **Validates: Requirements 3.3**

- [ ]* 13.3 Write property test for long content handling
  - **Property 8: Long Content Handling**
  - **Validates: Requirements 3.4**

- [x] 14. Create main entry point function

  - Implement `get_url_summary_response()` as the main entry point
  - Orchestrate the flow: validate URL → extract content → summarize → format response
  - Ensure consistent error response format across all error types
  - Return JSON-compatible dictionary with "response" or "error" keys
  - _Requirements: 5.4, 5.5_

- [ ]* 14.1 Write property test for error response structure
  - **Property 10: Error Response Structure**
  - **Validates: Requirements 4.3, 5.4**

- [ ]* 14.2 Write property test for response format consistency
  - **Property 11: Response Format Consistency**
  - **Validates: Requirements 5.5**

- [x] 15. Integrate URL summarizer with Flask application

  - Add `process_url_summarizer_request()` function to `app.py`
  - Import the URL summarizer agent module
  - Add URL detection logic to identify when user input contains URLs
  - Route URL-containing messages to the URL summarizer agent
  - Convert agent response to Flask jsonify format
  - Handle exceptions and return appropriate error responses
  - _Requirements: 5.3, 5.4, 5.5_

- [x] 16. Update frontend to support URL summarization

  - Add URL detection in `static/script.js` to identify URLs in user messages
  - Ensure chat interface displays URL summaries with proper formatting
  - Add visual feedback for URL processing (loading indicator)
  - Test that summaries display correctly in the chat history
  - Verify markdown-to-HTML rendering works properly
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 17. Add URL summarizer bot to sidebar and UI

  - Add "URL Summarizer" bot entry to the sidebar in `templates/index.html`
  - Create bot avatar and description in `botDescriptions` object in `static/script.js`
  - Add bot card to the models section on the main page
  - Ensure bot selection works and switches to URL summarizer mode
  - Test bot showcase page displays correctly
  - _Requirements: 4.1, 4.4_

- [x] 18. Update dependencies and configuration

  - Add `beautifulsoup4==4.12.3` to `requirements.txt`
  - Add `lxml==5.1.0` to `requirements.txt` (for faster HTML parsing)
  - Verify `requests` is already in requirements.txt
  - Ensure `.env.example` documents the GITHUB_TOKEN requirement
  - Update README.md with URL summarizer feature description
  - _Requirements: 7.1, 7.4_

- [x] 19. Checkpoint - Ensure all tests pass

  - Ensure all tests pass, ask the user if questions arise.

- [ ]* 20. Write unit tests for edge cases
  - Test empty URL input handling
  - Test non-existent page (404) handling
  - Test empty content extraction
  - Test authentication required (401/403) handling
  - Test JavaScript-heavy pages
  - Test various content types (news, blog, documentation)
  - Test missing GITHUB_TOKEN configuration
  - _Requirements: 1.2, 1.4, 2.4, 6.1, 6.2, 6.3, 6.4, 6.5, 7.2_

- [x] 21. Final integration testing and validation

  - Test end-to-end flow: URL input → summary display → database storage
  - Verify session management integration works correctly
  - Test with various real-world URLs (news sites, blogs, documentation)
  - Verify error messages are user-friendly and informative
  - Test that multiple URLs can be summarized in sequence
  - Confirm styling and layout consistency with existing UI
  - _Requirements: 4.4, 4.5, 6.1, 6.2, 6.3_

- [x] 22. Final Checkpoint - Ensure all tests pass

  - Ensure all tests pass, ask the user if questions arise.

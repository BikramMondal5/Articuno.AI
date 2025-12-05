## 🤖🪄 Articuno.AI v1.0 - "Interact. Innovate. Inspire with AI"

Articuno.AI is a cutting-edge AI-powered platform that brings together 20+ advanced AI models and specialized agents in one unified interface. From weather forecasting to code generation, video analysis to web development assistance - experience the future of AI interaction.

## 🌟 Key Features 

### 🎯 Specialized AI Agents
- 🌦️ **Articuno.AI Weather Agent** - Real-time weather updates, forecasts, and intelligent climate insights powered by OpenWeatherMap and Gemini AI
- 👨‍💻 **Bikram.AI** - Your friendly Full-stack Developer companion with expertise in React, Node.js, Three.js, and modern web technologies
- 📺 **ChatWithVideo** - Analyze and chat with YouTube videos using AI-powered transcript analysis
- 📚 **Wikipedia DeepSearch** - Quick access to Wikipedia knowledge with intelligent article summaries

### 🤖 20+ Advanced AI Models
Access industry-leading AI models including:
- **OpenAI**: GPT-4o, GPT-4o-mini
- **DeepSeek**: DeepSeek R1, DeepSeek V3
- **Google**: Gemini 2.0 Flash, Gemini 2.5 Flash
- **xAI**: Grok-3, Grok-3 Mini
- **Mistral**: Ministral 3B, Codestral 2501
- **Microsoft**: Phi-4, Phi-4 Mini
- **Meta**: Llama 3.1 8B, Llama 3.3 70B
- **Cohere**: Command A, Command R+

### 💾 Persistent Chat History
- **MongoDB Integration** - All conversations saved with full context
- **Session Management** - Create, retrieve, and manage multiple chat sessions
- **Chat Statistics** - Track message counts, timestamps, and conversation analytics
- **Session Search** - Find and resume previous conversations easily

### 🎨 Modern User Interface
- **Dark Theme Design** - Easy on the eyes with a sleek modern aesthetic
- **Organized Sidebar** - Categorized bot selection (Agents & AI Assistants)
- **Collapsible Categories** - Clean interface with expandable sections
- **Real-time Updates** - Instant message delivery and status indicators

### 🔧 Advanced Capabilities
- 🖼️ **Multi-modal Support** - Text, image, and audio processing
- 🎤 **Voice Input** - Speech-to-text transcription for hands-free interaction
- 📝 **Markdown Rendering** - Beautiful formatting for code and structured content
- 🔄 **Context Awareness** - AI remembers conversation history within sessions
- 📊 **Session Analytics** - Track usage statistics and conversation metrics

## 🛠️ Technologies Used

### Backend
- **Framework:** Flask 2.3.3
- **Database:** MongoDB (PyMongo 4.6.1)
- **AI Integration:** 
  - Azure AI Inference
  - Google Generative AI (Gemini)
  - LangChain & LangChain Community
  - OpenAI API
- **Audio Processing:** PyDub, FFmpeg, SpeechRecognition

### Frontend
- **Core:** HTML5, CSS3, JavaScript
- **Styling:** Modern dark theme with responsive design
- **Libraries:** 
  - Font Awesome 6.5.1 (icons)
  - GitHub Markdown CSS (markdown rendering)
  - EmailJS (email integration)

### APIs & Services
- **OpenWeatherMap** - Weather data and forecasts
- **GitHub Models** - AI model access via GitHub PAT
- **YouTube Transcript API** - Video transcript extraction
- **Wikipedia API** - Knowledge retrieval
- **Twilio** - SMS and voice alerts (optional)
- **Gmail & Slack** - Notification integrations (optional)

### Development Tools
- **Environment Management:** python-dotenv
- **Data Processing:** Requests, JSON utilities
- **Markdown:** Python-Markdown, Pygments (syntax highlighting)

## 🧠 Available AI Models & Agents

### 🤖 Specialized Agents (4)

#### Articuno.AI 🌦️
Your intelligent weather assistant powered by Gemini AI
- Real-time weather data via OpenWeatherMap API
- 3-day weather forecasts with detailed conditions
- Natural language weather queries
- Location detection from text
- Emergency weather alerts (with Twilio)
- Gmail & Slack integration for notifications

#### Bikram.AI 🚀
Your friendly Full-stack Developer companion
- Personality based on Bikram Mondal
- Expert in React, Node.js, Three.js, TypeScript
- Web development best practices
- Code debugging and optimization
- Learning through errors philosophy
- GitHub and open-source expertise

#### ChatWithVideo 📺
AI-powered YouTube video analysis
- Extract and analyze video transcripts
- Conversational Q&A about video content
- Session-based video memory
- Supports multiple YouTube URL formats
- Powered by GPT-4o via Azure

#### Wikipedia DeepSearch 📚
Instant access to Wikipedia knowledge
- Quick article summaries
- Intelligent information retrieval
- Natural language queries
- Context-aware responses

### 🧠 AI Assistants (16)

#### OpenAI Models
- **GPT-4o** - Flagship multimodal model with vision and advanced reasoning capabilities
- **GPT-4o-mini** - Fast, efficient variant perfect for quick responses and general tasks

#### DeepSeek Models
- **DeepSeek R1** - Open-weight reasoning model for complex problem-solving and coding
- **DeepSeek V3** - 671B parameter powerhouse with superior reasoning (deepseek-ai/DeepSeek-V3-0324)

#### Google Models
- **Gemini 2.0 Flash** - Fast multimodal LLM balancing speed and quality
- **Gemini 2.5 Flash** - Latest Gemini with enhanced reasoning and understanding

#### xAI Models
- **Grok-3** - 314B parameter model with witty personality and real-time knowledge
- **Grok-3 Mini** - Compact Grok variant with fast, engaging responses

#### Mistral AI Models
- **Ministral 3B** - Compact 3B parameter model optimized for efficiency
- **Codestral 2501** - 22B parameter specialist for code generation and technical tasks

#### Microsoft Models
- **Phi-4** - Microsoft's capable mid-size model with strong reasoning
- **Phi-4 Mini** - Lightweight version for fast inference

#### Meta Models
- **Meta Llama 3.1 8B** - Efficient open-source model for general tasks
- **Meta Llama 3.3 70B** - Powerful large-scale model with advanced capabilities

#### Cohere Models
- **Cohere Command A** - Enterprise-grade conversational AI
- **Cohere Command R+** - Enhanced reasoning and retrieval-augmented generation

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- MongoDB (local or cloud instance)
- FFmpeg (for audio processing)
- GitHub Personal Access Token (for GitHub Models)

### Step-by-Step Installation

1. **Clone the repository**
```bash
git clone https://github.com/BikramMondal5/Articuno.AI.git
cd Articuno.AI
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Install MongoDB**
   - **Local Installation:** Download from [mongodb.com](https://www.mongodb.com/try/download/community)
   - **Cloud:** Use MongoDB Atlas (free tier available)
   - Default connection: `mongodb://127.0.0.1:27017/`

4. **Install FFmpeg** (for voice input)
   - **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
   - **Linux:** `sudo apt install ffmpeg`
   - **macOS:** `brew install ffmpeg`

5. **Configure Environment Variables**
   
   Create a `.env` file in the root directory:
   ```env
   # Required
   GITHUB_TOKEN=your_github_personal_access_token
   GEMINI_API_KEY=your_google_gemini_api_key
   
   # Optional - Weather Features
   OPENWEATHER_API_KEY=your_openweather_api_key
   
   # Optional - Voice Alerts
   TWILIO_ACCOUNT_SID=your_twilio_account_sid
   TWILIO_AUTH_TOKEN=your_twilio_auth_token
   TWILIO_PHONE_NUMBER=your_twilio_phone_number
   
   # Optional - Database
   MONGODB_URI=mongodb://127.0.0.1:27017/
   
   # Optional - Flask
   SECRET_KEY=your_secret_key_for_sessions
   
   # Optional - FFmpeg Path (if not in PATH)
   FFMPEG_PATH=C:\Program Files\ffmpeg\bin\ffmpeg.exe
   ```

6. **Get API Keys**
   - **GitHub Token:** [Generate PAT](https://github.com/settings/tokens) with appropriate scopes
   - **Gemini API:** Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - **OpenWeather:** Free key from [openweathermap.org](https://openweathermap.org/api)

7. **Start MongoDB**
   ```bash
   # If using local MongoDB
   mongod
   ```

8. **Run the application**
   ```bash
   python app.py
   ```

9. **Access the platform**
   
   Open your browser and navigate to: `http://127.0.0.1:5000/`

### Database Management

**Clear chat history:**
```bash
python clear_sessions.py
```

**Test MongoDB connection:**
```bash
python test_mongodb.py
```

## 📁 Project Structure

```
Articuno.AI/
├── agent/                      # AI model integrations
│   ├── articuno_weather.py    # Weather agent
│   ├── Bikram_AI.py           # Developer assistant
│   ├── ChatWithVideo.py       # YouTube video analyzer
│   ├── wikipedia_agent.py     # Wikipedia search
│   ├── gpt_4o.py              # GPT-4o integration
│   ├── gpt_4o_mini.py         # GPT-4o-mini integration
│   ├── gemini_flash.py        # Gemini 2.0 Flash
│   ├── gemini_2.5_flash.py    # Gemini 2.5 Flash
│   ├── DeepSeek_V3_0324.py    # DeepSeek V3
│   ├── grok3.py               # Grok-3
│   ├── grok_3_mini.py         # Grok-3 Mini
│   ├── Ministral_3B.py        # Ministral 3B
│   ├── Codestral_2501.py      # Codestral 2501
│   ├── Phi_4.py               # Phi-4
│   ├── Phi_4_mini.py          # Phi-4 Mini
│   ├── Meta_Llama_3.1_8B.py   # Llama 3.1 8B
│   ├── Meta_Llama_3.3_70B.py  # Llama 3.3 70B
│   ├── cohere_command_a.py    # Cohere Command A
│   └── Cohere_command_r_plus.py # Cohere Command R+
├── database/                   # MongoDB integration
│   ├── __init__.py
│   └── db_manager.py          # Database operations
├── static/                     # Frontend assets
│   ├── script.js              # Main JavaScript
│   ├── session_manager.js     # Session management
│   ├── styles.css             # Styling
│   └── icons/                 # UI icons and images
├── templates/                  # HTML templates
│   └── index.html             # Main interface
├── app.py                      # Flask application
├── requirements.txt            # Python dependencies
├── clear_sessions.py          # Database cleanup utility
├── test_mongodb.py            # MongoDB connection test
└── README.md                   # Documentation
```

## 🚀 Usage

### Basic Interaction
1. Select an AI model or agent from the sidebar
2. Type your message or click the microphone for voice input
3. For image-capable models (GPT-4o, Gemini), upload images
4. View responses with markdown formatting and syntax highlighting

### Session Management
- **New Session:** Click "New Chat" to start fresh
- **Session History:** Access previous conversations from the sidebar
- **Session Stats:** View message counts and timestamps
- **Delete Sessions:** Remove unwanted chat history

### Weather Queries (Articuno.AI)
```
"What's the weather in Tokyo?"
"Give me a 3-day forecast for London"
"Will it rain in Seattle today?"
```

### Video Analysis (ChatWithVideo)
```
1. Paste YouTube URL
2. Wait for transcript extraction
3. Ask questions about the video content
```

### Developer Help (Bikram.AI)
```
"How do I implement useState in React?"
"Explain Node.js event loop"
"Best practices for Three.js optimization"
```

## 🔧 API Endpoints

### Chat
- `POST /api/chat` - Send message to AI model
- `POST /api/transcribe` - Audio to text conversion

### Sessions
- `POST /api/session/new` - Create new session
- `GET /api/session/history/<session_id>` - Get chat history
- `GET /api/session/list` - List all sessions
- `GET /api/session/<session_id>/stats` - Session statistics
- `DELETE /api/session/<session_id>/delete` - Delete session

### Weather
- `GET /api/weather` - Fetch weather data

### Search
- `GET /api/search` - Search conversations

## 🌟 Features in Detail

### Multi-modal Capabilities
- **Text:** All models support text input/output
- **Images:** GPT-4o, Gemini models support image analysis
- **Voice:** Speech-to-text for hands-free interaction
- **Video:** ChatWithVideo analyzes YouTube content

### Session Persistence
- All conversations automatically saved to MongoDB
- Resume chats anytime with full context
- Search through message history
- Export chat sessions (future feature)

### Markdown Support
- Code syntax highlighting with Pygments
- Tables, lists, and formatting
- LaTeX math equations (future feature)
- Embedded media support

## ☎️ Contact
For queries, feedback, or collaboration opportunities:
- **Email:** codesnippets45@gmail.com
- **GitHub:** [@BikramMondal5](https://github.com/BikramMondal5)

## 🤝 Contributing
Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit your changes** (`git commit -m 'Add some AmazingFeature'`)
4. **Push to the branch** (`git push origin feature/AmazingFeature`)
5. **Open a Pull Request**

### Areas for Contribution
- Adding new AI model integrations
- Improving UI/UX design
- Database optimization
- API documentation
- Bug fixes and testing
- Feature enhancements

## 🙏 Acknowledgments
- OpenAI, Google, xAI, Microsoft, Meta, Cohere, Mistral AI for their amazing AI models
- GitHub Models for model access infrastructure
- MongoDB for database solutions
- The open-source community for various libraries and tools

## 📊 Project Status
- **Version:** 1.0
- **Status:** Active Development
- **Last Updated:** December 2025

---
## 📜 License
This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

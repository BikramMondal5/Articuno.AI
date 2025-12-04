import os
import re
from flask import jsonify
import markdown
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()

# API configuration
ENDPOINT = "https://models.github.ai/inference"
MODEL_NAME = "openai/gpt-4o"
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')

# Memory storage for video transcripts per session
video_memory = {}

# Validate token
if not GITHUB_TOKEN:
    print("WARNING: GITHUB_TOKEN environment variable is not set for ChatWithVideo!")
    client = None
else:
    try:
        # Azure AI Inference client configuration
        client = ChatCompletionsClient(
            endpoint=ENDPOINT,
            credential=AzureKeyCredential(GITHUB_TOKEN),
        )
    except Exception as e:
        print(f"Error initializing Azure AI client for ChatWithVideo: {e}")
        client = None

def extract_video_id(youtube_url):
    """Extract the video ID from a YouTube URL."""
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',  # Standard and short URLs
        r'(?:embed\/)([0-9A-Za-z_-]{11})',   # Embed URLs
        r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})'  # youtu.be URLs
    ]
    
    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)
    
    return None

def get_transcript(video_id):
    """Get transcript from YouTube video."""
    try:
        # Initialize the API client
        ytt_api = YouTubeTranscriptApi()
        
        # Try to get transcript - first try English, then fall back to other languages
        try:
            fetched_transcript = ytt_api.fetch(video_id, languages=['en', 'hi', 'bn'])
            full_text = " ".join([snippet.text for snippet in fetched_transcript.snippets])
            return {"success": True, "transcript": full_text}
        except Exception as fetch_error:
            # Try to list available transcripts and get the first one
            transcript_list = ytt_api.list(video_id)
            
            # Try to find any available transcript
            for transcript in transcript_list:
                try:
                    fetched = transcript.fetch()
                    full_text = " ".join([snippet.text for snippet in fetched.snippets])
                    return {"success": True, "transcript": full_text}
                except:
                    continue
            
            return {"success": False, "error": "No transcript found for this video."}
            
    except NoTranscriptFound:
        return {"success": False, "error": "No transcript found for this video."}
    except TranscriptsDisabled:
        return {"success": False, "error": "Transcripts are disabled for this video."}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "error": f"Error fetching transcript: {str(e)}"}

def summarize_transcript(transcript):
    """Use GPT-4o to summarize the transcript."""
    if client is None:
        return {"success": False, "error": "Azure AI client is not initialized. Please check GITHUB_TOKEN."}
    
    try:
        response = client.complete(
            messages=[
                SystemMessage("You're an advanced AI designed to summarize YouTube videos. Extract key information from the transcript including Title of the video, speaker, main topics, key takeaways, Timestamps for Notable Moments, Quotes and Impactful Statements, Analysis Sentiment if possible and notable insights. Format your response using Markdown with proper headings, bullet points, add interactive & appropriate emojis and sections for easy reading. Include a brief overview, key points, and conclusion."),
                UserMessage(transcript),
            ],
            temperature=0.7,
            top_p=1.0,
            max_tokens=1500,
            model=MODEL_NAME
        )
        
        return {"success": True, "summary": response.choices[0].message.content}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "error": f"Summarization error: {str(e)}"}

def answer_question_about_video(question, session_id):
    """Answer questions about the video using the stored transcript."""
    if client is None:
        return {"success": False, "error": "Azure AI client is not initialized. Please check GITHUB_TOKEN."}
    
    # Check if we have a transcript in memory for this session
    if session_id not in video_memory or 'transcript' not in video_memory[session_id]:
        return {
            "success": False, 
            "error": "No video transcript found in memory. Please analyze a video first."
        }
    
    transcript = video_memory[session_id]['transcript']
    video_id = video_memory[session_id].get('video_id', 'unknown')
    
    try:
        # Build conversation history for context
        conversation_history = video_memory[session_id].get('conversation_history', [])
        
        # Create messages for the AI
        messages = [
            SystemMessage(
                "You are an AI assistant specialized in answering questions about YouTube videos. "
                "You have access to the full transcript of a video. Use this transcript to provide accurate, "
                "detailed answers to the user's questions. If the information is not in the transcript, "
                "say so honestly. Format your responses using Markdown for better readability."
            ),
            UserMessage(f"Here is the video transcript:\n\n{transcript}\n\n")
        ]
        
        # Add conversation history
        for msg in conversation_history[-6:]:  # Keep last 3 exchanges (6 messages)
            if msg['role'] == 'user':
                messages.append(UserMessage(msg['content']))
            else:
                messages.append(SystemMessage(f"Previous response: {msg['content']}"))
        
        # Add current question
        messages.append(UserMessage(question))
        
        response = client.complete(
            messages=messages,
            temperature=0.7,
            top_p=1.0,
            max_tokens=1000,
            model=MODEL_NAME
        )
        
        answer = response.choices[0].message.content
        
        # Store in conversation history
        conversation_history.append({'role': 'user', 'content': question})
        conversation_history.append({'role': 'assistant', 'content': answer})
        video_memory[session_id]['conversation_history'] = conversation_history
        
        return {"success": True, "answer": answer}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "error": f"Error answering question: {str(e)}"}

def process_chatwithvideo_request(user_input, session_id=None):
    """Process ChatWithVideo request - either analyze a video or answer questions about it."""
    if not user_input:
        return jsonify({"success": False, "error": "Please provide input"}), 400
    
    # Check if input is a YouTube URL
    video_id = extract_video_id(user_input)
    
    if video_id:
        # This is a YouTube URL - analyze the video
        # Get transcript
        transcript_result = get_transcript(video_id)
        
        if not transcript_result["success"]:
            return jsonify({"success": False, "error": transcript_result["error"]}), 400
        
        # Store transcript in memory for this session
        if session_id:
            video_memory[session_id] = {
                'transcript': transcript_result['transcript'],
                'video_id': video_id,
                'conversation_history': []
            }
        
        # Summarize transcript
        summary_result = summarize_transcript(transcript_result["transcript"])
        
        if not summary_result["success"]:
            return jsonify({"success": False, "error": summary_result["error"]}), 500
        
        # Convert markdown to HTML
        summary_html = markdown.markdown(summary_result["summary"])
        
        # Add helpful note about asking questions
        summary_html += "<br><br><p style='color: #a0a0a0; font-style: italic;'>💬 You can now ask me questions about this video!</p>"
        
        return jsonify({
            "success": True,
            "video_id": video_id,
            "response": summary_html
        }), 200
    else:
        # This is a question about the video
        
        if not session_id:
            return jsonify({
                "success": False, 
                "error": "No session ID provided. Cannot retrieve video context."
            }), 400
        
        answer_result = answer_question_about_video(user_input, session_id)
        
        if not answer_result["success"]:
            return jsonify({"success": False, "error": answer_result["error"]}), 400
        
        # Convert markdown to HTML
        answer_html = markdown.markdown(answer_result["answer"])
        
        return jsonify({
            "success": True,
            "response": answer_html
        }), 200

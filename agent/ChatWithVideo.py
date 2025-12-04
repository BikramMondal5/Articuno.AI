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

# Validate token
if not GITHUB_TOKEN:
    print("WARNING: GITHUB_TOKEN environment variable is not set for ChatWithVideo!")
    client = None
else:
    print(f"ChatWithVideo: GITHUB_TOKEN loaded successfully")
    try:
        # Azure AI Inference client configuration
        client = ChatCompletionsClient(
            endpoint=ENDPOINT,
            credential=AzureKeyCredential(GITHUB_TOKEN),
        )
        print("ChatWithVideo: Azure AI Inference client initialized successfully")
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
        print(f"Fetching transcript for video ID: {video_id}")
        # Initialize the API client
        ytt_api = YouTubeTranscriptApi()
        
        # Try to get transcript - first try English, then fall back to other languages
        try:
            print("Attempting to fetch transcript with preferred languages: en, hi, bn")
            fetched_transcript = ytt_api.fetch(video_id, languages=['en', 'hi', 'bn'])
            full_text = " ".join([snippet.text for snippet in fetched_transcript.snippets])
            print(f"Transcript fetched successfully: {len(full_text)} characters")
            return {"success": True, "transcript": full_text}
        except Exception as fetch_error:
            print(f"Error fetching with preferred languages: {fetch_error}")
            # Try to list available transcripts and get the first one
            print("Trying to list all available transcripts...")
            transcript_list = ytt_api.list(video_id)
            
            # Try to find any available transcript
            for transcript in transcript_list:
                try:
                    fetched = transcript.fetch()
                    full_text = " ".join([snippet.text for snippet in fetched.snippets])
                    print(f"Transcript found in {transcript.language}: {len(full_text)} characters")
                    return {"success": True, "transcript": full_text}
                except:
                    continue
            
            return {"success": False, "error": "No transcript found for this video."}
            
    except NoTranscriptFound:
        print("NoTranscriptFound exception")
        return {"success": False, "error": "No transcript found for this video."}
    except TranscriptsDisabled:
        print("TranscriptsDisabled exception")
        return {"success": False, "error": "Transcripts are disabled for this video."}
    except Exception as e:
        print(f"Transcript fetch error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": f"Error fetching transcript: {str(e)}"}

def summarize_transcript(transcript):
    """Use GPT-4o to summarize the transcript."""
    if client is None:
        return {"success": False, "error": "Azure AI client is not initialized. Please check GITHUB_TOKEN."}
    
    try:
        print(f"\n=== Attempting to summarize transcript ===")
        print(f"Endpoint: {ENDPOINT}")
        print(f"Model: {MODEL_NAME}")
        print(f"Transcript length: {len(transcript)} characters")
        print(f"Client type: {type(client)}")
        
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
        
        print(f"Response received successfully")
        print(f"Response type: {type(response)}")
        return {"success": True, "summary": response.choices[0].message.content}
    except Exception as e:
        print(f"\n=== Error during summarization ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
        print("=================================\n")
        return {"success": False, "error": f"Summarization error: {str(e)}"}

def process_chatwithvideo_request(youtube_url):
    """Process ChatWithVideo request with YouTube URL."""
    print("\n=== ChatWithVideo request ===")
    print(f"YouTube URL: {youtube_url}")
    
    if not youtube_url:
        return jsonify({"success": False, "error": "Please enter a YouTube URL"}), 400
    
    video_id = extract_video_id(youtube_url)
    print(f"Extracted video ID: {video_id}")
    
    if not video_id:
        return jsonify({"success": False, "error": "Invalid YouTube URL. Please check and try again."}), 400
    
    # Get transcript
    print("Fetching transcript...")
    transcript_result = get_transcript(video_id)
    print(f"Transcript result: success={transcript_result['success']}")
    
    if not transcript_result["success"]:
        print(f"Transcript error: {transcript_result['error']}")
        return jsonify({"success": False, "error": transcript_result["error"]}), 400
    
    print(f"Transcript fetched: {len(transcript_result['transcript'])} characters")
    
    # Summarize transcript
    print("Starting summarization...")
    summary_result = summarize_transcript(transcript_result["transcript"])
    print(f"Summarization result: success={summary_result['success']}")
    
    if not summary_result["success"]:
        print(f"Summarization error: {summary_result['error']}")
        return jsonify({"success": False, "error": summary_result["error"]}), 500
    
    # Convert markdown to HTML
    print("Converting markdown to HTML...")
    summary_html = markdown.markdown(summary_result["summary"])
    
    print("Returning successful response")
    return jsonify({
        "success": True,
        "video_id": video_id,
        "response": summary_html
    }), 200

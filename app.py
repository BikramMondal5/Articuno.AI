from flask import Flask, render_template, request, jsonify
import markdown
import os
import requests
import json
import base64
import speech_recognition as sr
import io
import tempfile 
import uuid
from pydub import AudioSegment
import google.generativeai as genai
import re
import traceback
from dotenv import load_dotenv
from agent.wikipedia_agent import get_wikipedia_response

# Import GPT-4o-mini function with proper module name
import sys
sys.path.append(os.path.dirname(__file__))
try:
    from agent.gpt_4o_mini import get_gpt4o_mini_response
except ImportError:
    # Fallback if import fails
    def get_gpt4o_mini_response(message):
        return "GPT-4o-mini is currently unavailable."

# Import Grok-3 function
try:
    from agent.grok3 import get_grok3_response
except ImportError:
    # Fallback if import fails
    def get_grok3_response(message):
        return "Grok-3 is currently unavailable."

# Import Grok-3 Mini function
try:
    from agent.grok_3_mini import get_grok3_mini_response
except ImportError:
    # Fallback if import fails
    def get_grok3_mini_response(message):
        return "Grok-3 Mini is currently unavailable."

# Import Ministral 3B function
try:
    from agent.Ministral_3B import get_ministral_3b_response
except ImportError:
    # Fallback if import fails
    def get_ministral_3b_response(message):
        return "Ministral 3B is currently unavailable."

# Import Codestral 2501 function
try:
    from agent.Codestral_2501 import get_codestral_2501_response
except ImportError:
    # Fallback if import fails
    def get_codestral_2501_response(message):
        return "Codestral 2501 is currently unavailable."

# Import DeepSeek V3 0324 function
try:
    from agent.DeepSeek_V3_0324 import get_deepseek_v3_response
except ImportError:
    # Fallback if import fails
    def get_deepseek_v3_response(message):
        return "DeepSeek V3 is currently unavailable."

# Import Articuno Weather function
try:
    from agent.articuno_weather import get_articuno_weather_response
except ImportError:
    # Fallback if import fails
    def get_articuno_weather_response(message, image_data=None):
        return jsonify({"error": "Articuno Weather is currently unavailable."}), 500

# Import Gemini Flash function
try:
    from agent.gemini_flash import get_gemini_flash_response
except ImportError:
    # Fallback if import fails
    def get_gemini_flash_response(message, image_data=None):
        return jsonify({"error": "Gemini 2.0 Flash is currently unavailable."}), 500

# Import Gemini 2.5 Flash function
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("gemini_25_flash", "agent/gemini_2.5_flash.py")
    gemini_25_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gemini_25_module)
    get_gemini_25_flash_response = gemini_25_module.get_gemini_flash_response
except Exception:
    # Fallback if import fails
    def get_gemini_25_flash_response(message, image_data=None):
        return jsonify({"error": "Gemini 2.5 Flash is currently unavailable."}), 500

# Import GPT-4o function
try:
    from agent.gpt_4o import get_gpt4o_response
except ImportError:
    # Fallback if import fails
    def get_gpt4o_response(message, image_data=None):
        return jsonify({"error": "GPT-4o is currently unavailable."}), 500

# Load environment variables from .env file
load_dotenv()

# Set FFmpeg path explicitly
try:
    ffmpeg_path = os.getenv("FFMPEG_PATH")
    
    if os.path.isfile(ffmpeg_path):
        AudioSegment.converter = ffmpeg_path
        print(f"FFmpeg found at: {ffmpeg_path}")
    else:
        possible_ffmpeg_paths = [
            r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
            r"C:\ffmpeg\bin\ffmpeg.exe",
            os.path.expanduser("~") + r"\ffmpeg\bin\ffmpeg.exe"
        ]
        
        ffmpeg_path = None
        for path in possible_ffmpeg_paths:
            if os.path.isfile(path):
                ffmpeg_path = path
                break
        
        if ffmpeg_path:
            AudioSegment.converter = ffmpeg_path
            print(f"FFmpeg found at: {ffmpeg_path}")
        else:
            print("FFmpeg not found in common locations. Relying on PATH environment variable.")
except Exception as e:
    print(f"Error setting FFmpeg path: {str(e)}")

# Configure Google Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Configure OpenWeather API
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"

# Initializing the app
app = Flask(__name__)

@app.route('/', methods=["GET"])
def home_page():
    return render_template('index.html')

@app.route('/api/weather', methods=["GET"])
def get_weather():
    """API endpoint for fetching weather data"""
    # Get request parameters
    location = request.args.get('location')
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    request_type = request.args.get('type', 'current')  # 'current' or 'forecast'
    
    if not location and not (lat and lon):
        return jsonify({"error": "Missing location or coordinates"}), 400
    
    try:
        # Build API URL based on request type
        if request_type == 'current':
            endpoint = f"{OPENWEATHER_BASE_URL}/weather"
        else:
            endpoint = f"{OPENWEATHER_BASE_URL}/forecast"
        
        # Build request parameters
        params = {
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"  # Use metric units (Celsius)
        }
        
        # Add location or coordinates to the parameters
        if location:
            params["q"] = location
        else:
            params["lat"] = lat
            params["lon"] = lon
        
        # Make the request to the OpenWeather API
        print(f"Making request to {endpoint} with params: {params}")
        response = requests.get(endpoint, params=params)
        
        # Check for errors
        if response.status_code != 200:
            error_message = response.json().get('message', 'Unknown error')
            print(f"Error from OpenWeather API: {response.status_code} - {error_message}")
            return jsonify({
                "error": f"Weather API error: {response.status_code} - {error_message}",
                "success": False
            }), response.status_code
        
        # Return the weather data
        data = response.json()
        return jsonify(data)
    
    except Exception as e:
        print(f"Error fetching weather data: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e), "success": False}), 500

def get_image_data_url(image_data, image_format):
    """
    Converts image binary data to a data URL string.
    
    Args:
        image_data (bytes): The binary audio data
        image_format (str): The format of the image file (jpg, png, etc)
        
    Returns:
        str: The data URL of the image
    """
    encoded_image = base64.b64encode(image_data).decode("utf-8")
    return f"data:image/{image_format};base64,{encoded_image}"

def transcribe_audio(audio_data):
    """
    Transcribes audio data to text using SpeechRecognition.
    
    Args:
        audio_data (bytes): The binary audio data
        
    Returns:
        str: The transcribed text
    """
    recognizer = sr.Recognizer()
    
    # Generate temporary filenames with random UUID to avoid conflicts
    temp_input_filename = os.path.join(tempfile.gettempdir(), f"audio_input_{uuid.uuid4().hex}.webm")
    temp_wav_filename = os.path.join(tempfile.gettempdir(), f"audio_converted_{uuid.uuid4().hex}.wav")
    
    try:
        # Write the input audio data to a temporary file
        with open(temp_input_filename, 'wb') as f:
            f.write(audio_data)
        
        print(f"Audio file saved to: {temp_input_filename}")
        print(f"Audio file size: {os.path.getsize(temp_input_filename)} bytes")
        
        # Try multiple approaches to convert the audio
        try:
            print("Attempting to convert audio with pydub...")
            
            # Tell pydub where to find FFmpeg explicitly if not set yet
            if not hasattr(AudioSegment, 'converter') or not AudioSegment.converter:
                # Try to locate ffmpeg in system PATH
                import subprocess
                try:
                    ffmpeg_path = subprocess.check_output(['where', 'ffmpeg'], text=True).strip().split('\n')[0]
                    AudioSegment.converter = ffmpeg_path
                    print(f"Found ffmpeg at: {ffmpeg_path}")
                except Exception as e:
                    print(f"Could not find ffmpeg in PATH: {str(e)}")
            
            # Try to read as WebM (most common browser recording format)
            audio = AudioSegment.from_file(temp_input_filename, format="webm")
            print("Successfully read as WebM")
        except Exception as webm_error:
            print(f"Error reading as WebM: {str(webm_error)}")
            try:
                # Try to read as Ogg
                audio = AudioSegment.from_file(temp_input_filename, format="ogg")
                print("Successfully read as Ogg")
            except Exception as ogg_error:
                print(f"Error reading as Ogg: {str(ogg_error)}")
                try:
                    # Try to read as WAV
                    audio = AudioSegment.from_wav(temp_input_filename)
                    print("Successfully read as WAV")
                except Exception as wav_error:
                    print(f"Error reading as WAV: {str(wav_error)}")
                    # Try as a generic file and let pydub detect format
                    try:
                        audio = AudioSegment.from_file(temp_input_filename)
                        print("Successfully read as generic file")
                    except Exception as generic_error:
                        # As a last resort, try direct conversion with ffmpeg
                        print(f"Error reading as generic file: {str(generic_error)}")
                        print("Attempting direct conversion with ffmpeg subprocess...")
                        import subprocess
                        try:
                            subprocess.run([
                                'ffmpeg', '-y',
                                '-i', temp_input_filename,
                                '-ar', '16000', '-ac', '1',
                                temp_wav_filename
                            ], check=True)
                            print("Successfully converted with ffmpeg subprocess")
                        except Exception as ffmpeg_error:
                            print(f"Error with ffmpeg subprocess: {str(ffmpeg_error)}")
                            raise Exception(f"Failed to convert audio file: {str(generic_error)}")
        
        # Export to WAV if we didn't already use the subprocess approach
        if 'audio' in locals():
            print("Exporting to WAV format...")
            audio.export(temp_wav_filename, format="wav")
            print(f"Exported to {temp_wav_filename}")
        
        print(f"Converted WAV file size: {os.path.getsize(temp_wav_filename)} bytes")
        
        # Use the converted WAV file for recognition
        with sr.AudioFile(temp_wav_filename) as source:
            print("Loading audio into recognizer...")
            audio_data = recognizer.record(source)
            
            # Use Google's speech recognition service
            print("Sending to Google speech recognition...")
            text = recognizer.recognize_google(audio_data)
            print(f"Transcription result: {text}")
            return text
    except sr.UnknownValueError:
        print("Speech Recognition could not understand the audio")
        return "Speech Recognition could not understand the audio"
    except sr.RequestError as e:
        print(f"Could not request results from Speech Recognition service: {str(e)}")
        return f"Could not request results from Speech Recognition service: {str(e)}"
    except Exception as e:
        print(f"Error processing audio: {str(e)}")
        return f"Error processing audio: {str(e)}"
    finally:
        # Clean up the temporary files
        try:
            if os.path.exists(temp_input_filename):
                os.remove(temp_input_filename)
                print(f"Removed temporary input file: {temp_input_filename}")
            if os.path.exists(temp_wav_filename):
                os.remove(temp_wav_filename)
                print(f"Removed temporary WAV file: {temp_wav_filename}")
        except Exception as e:
            print(f"Error cleaning up temporary files: {str(e)}")

@app.route('/api/transcribe', methods=["POST"])
def transcribe():
    """API endpoint for handling audio transcription"""
    try:
        # Get audio data from request
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        
        audio_file = request.files['audio']
        audio_data = audio_file.read()
        
        if len(audio_data) == 0:
            return jsonify({"error": "Empty audio file"}), 400
        
        # Process the audio data
        transcribed_text = transcribe_audio(audio_data)
        
        return jsonify({"transcription": transcribed_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=["POST"])
def chat():
    # Get JSON data from the request
    data = request.json
    user_input = data.get('message', '')
    image_data = data.get('image', None)
    bot_name = data.get('bot', 'Articuno.AI')
    
    if not user_input and not image_data:
        return jsonify({"error": "No message or image provided"}), 400
    
    try:
        # Check which bot is selected and use appropriate API
        if bot_name == "Articuno.AI":
            # Use Articuno Weather agent
            return get_articuno_weather_response(user_input, image_data)
        elif bot_name == "GPT-4o":
            # Use GPT-4o agent
            return get_gpt4o_response(user_input, image_data)
        elif bot_name == "Wikipedia Bot":
            # Use Wikipedia agent for search
            return process_wikipedia_request(user_input)
        elif bot_name == "GPT-4o-mini":
            # Use GPT-4o-mini from GitHub Models
            return process_gpt4o_mini_request(user_input)
        elif bot_name == "Grok-3":
            # Use Grok-3 from GitHub Models
            return process_grok3_request(user_input)
        elif bot_name == "Grok-3 Mini":
            # Use Grok-3 Mini from GitHub Models
            return process_grok3_mini_request(user_input)
        elif bot_name == "Ministral 3B":
            # Use Ministral 3B from GitHub Models
            return process_ministral_3b_request(user_input)
        elif bot_name == "Codestral 2501":
            # Use Codestral 2501 from GitHub Models
            return process_codestral_2501_request(user_input)
        elif bot_name == "DeepSeek V3":
            # Use DeepSeek V3 0324 from GitHub Models
            return process_deepseek_v3_request(user_input)
        elif bot_name == "Gemini 2.5 Flash":
            # Use Gemini 2.5 Flash agent
            return get_gemini_25_flash_response(user_input, image_data)
        elif bot_name == "Gemini 2.0 Flash" or bot_name.lower() == "gemini" or (image_data and bot_name != "Articuno.AI"):
            # Use Gemini 2.0 Flash agent
            return get_gemini_flash_response(user_input, image_data)
        else:
            # Use GPT-4o as fallback
            return get_gpt4o_response(user_input, image_data)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===================================================================
# NOTE: The following model-specific functions have been moved to separate agent files:
# - Articuno Weather functions -> agent/articuno_weather.py
# - Gemini Flash functions -> agent/gemini_flash.py  
# - GPT-4o functions -> agent/gpt_4o.py
# ===================================================================

def old_format_weather_data_for_gemini(weather_data, location):
    """
    Formats weather data into a structured prompt for Gemini model.
    
    Args:
        weather_data (dict): Weather data from OpenWeather API
        location (str): The location name
        
    Returns:
        str: Formatted weather data prompt
    """
    if "error" in weather_data:
        return f"Error: {weather_data['error']}"
    
    try:
        current = weather_data["current"]
        
        # Extract current weather data
        temp = current["main"]["temp"]
        feels_like = current["main"]["feels_like"]
        humidity = current["main"]["humidity"]
        weather_desc = current["weather"][0]["description"]
        weather_main = current["weather"][0]["main"]
        wind_speed = current["wind"]["speed"]
        
        # Get pressure and visibility if available
        pressure = current["main"].get("pressure", "N/A")
        visibility = current.get("visibility", "N/A")
        if visibility != "N/A":
            visibility = visibility / 1000  # Convert from meters to kilometers
        
        # Extract sunrise and sunset times if available
        sunrise = sunset = "N/A"
        if "sys" in current and "sunrise" in current["sys"] and "sunset" in current["sys"]:
            sunrise_timestamp = current["sys"]["sunrise"]
            sunset_timestamp = current["sys"]["sunset"]
            from datetime import datetime
            sunrise = datetime.fromtimestamp(sunrise_timestamp).strftime('%H:%M')
            sunset = datetime.fromtimestamp(sunset_timestamp).strftime('%H:%M')
        
        # Extract location data
        city_name = current["name"]
        country = current["sys"]["country"]
        
        # Extract forecast if available
        forecast_text = ""
        if "forecast" in weather_data:
            forecast = weather_data["forecast"]
            forecast_text = "\n\nForecast for next few days:\n"
            
            # Group forecast by day
            day_forecasts = {}
            for item in forecast["list"]:
                dt = item["dt"]
                date = item["dt_txt"].split(" ")[0]
                
                if date not in day_forecasts:
                    day_forecasts[date] = []
                
                day_forecasts[date].append(item)
            
            # Generate a summary for each day
            for date, items in list(day_forecasts.items())[:3]:  # Limit to 3 days
                # Calculate average temp for the day
                avg_temp = sum(item["main"]["temp"] for item in items) / len(items)
                
                # Calculate min and max temps
                min_temp = min(item["main"]["temp_min"] for item in items)
                max_temp = max(item["main"]["temp_max"] for item in items)
                
                # Find most common weather condition
                conditions = [item["weather"][0]["main"] for item in items]
                most_common_condition = max(set(conditions), key=conditions.count)
                
                # Get detailed description of most common condition
                condition_desc = next((item["weather"][0]["description"] for item in items 
                                      if item["weather"][0]["main"] == most_common_condition), most_common_condition)
                
                # Calculate average precipitation probability if available
                precipitation_prob = 0
                precipitation_count = 0
                for item in items:
                    if "pop" in item:
                        precipitation_prob += item["pop"]
                        precipitation_count += 1
                
                if precipitation_count > 0:
                    avg_precipitation_prob = (precipitation_prob / precipitation_count) * 100  # Convert to percentage
                    precipitation_text = f", {avg_precipitation_prob:.0f}% chance of precipitation"
                else:
                    precipitation_text = ""
                
                forecast_text += f"- {date}: {min_temp:.1f}°C to {max_temp:.1f}°C (avg: {avg_temp:.1f}°C), {condition_desc}{precipitation_text}\n"
        
        # Format the weather data as a prompt for Gemini
        prompt = f"""Weather data for {city_name}, {country} (User asked about: {location}):
        
Current conditions:
- Temperature: {temp}°C (feels like {feels_like}°C)
- Weather: {weather_desc} ({weather_main})
- Humidity: {humidity}%
- Wind speed: {wind_speed} m/s
- Air pressure: {pressure} hPa
- Visibility: {visibility if visibility != "N/A" else "N/A"} km
- Sunrise: {sunrise}
- Sunset: {sunset}
{forecast_text}

Now, provide a friendly and helpful response about this weather information to the user. Be conversational and engaging. Use emojis appropriately to enhance the message. Include practical advice based on the weather conditions (what to wear, precautions to take, etc.). End with a friendly follow-up question.

Remember to present the information in a well-structured way, including:
1. A warm greeting that references the location
2. Current weather conditions with a friendly tone
3. Forecast information for the next few days
4. Practical advice based on the conditions
5. A friendly question or suggestion to keep the conversation going
"""
        return prompt
    except Exception as e:
        return f"Error formatting weather data: {str(e)}"

# OLD FUNCTION - Now handled by agent/articuno_weather.py
# def process_articuno_weather_request(user_input, image_data=None):
def process_articuno_weather_request_OLD(user_input, image_data=None):
    """DEPRECATED: Process chat request specifically for Articuno.AI as a weather assistant
    This function has been moved to agent/articuno_weather.py"""
    try:
        # Configure the model
        generation_config = {
            "temperature": 0.7,
            "top_p": 1,
            "top_k": 32,
            "max_output_tokens": 1000,
        }
        
        # Create weather-focused system prompt
        weather_system_prompt = """Welcome to Articuno.AI – your friendly weather assistant! ❄️
You're here to help users explore weather updates with style, clarity, and a touch of personality 😊

Your Role:

You are a polite, knowledgeable, and conversational assistant that specializes in weather information.

Your answers should be concise, friendly, and easy to understand – even for someone not familiar with weather terms.

You may use emojis sparingly to enhance friendliness, but never in the middle of sentences.

If a user shares a location, provide current weather info and a quick summary of the next 2–3 days.

Always address the user's specific question about weather and provide helpful context based on the conditions.

Provide practical advice based on the weather conditions (e.g., "Don't forget your umbrella!" for rain).

Tone & Style:

Be warm, responsive, and conversational - like a friendly meteorologist.

Use short paragraphs and bullet points if helpful.

End most responses with a gentle question or suggestion to keep the flow going.
(e.g., "Would you like a forecast for the next few days?" or "Is there anything else about the weather you'd like to know?")

Example Starters:

🌤️ "Looks like it's sunny in [Location]! Want to know what's coming this weekend?"

🌧️ "Rain ahead in [Location]! Don't forget your umbrella ☔ Ready for a 3-day forecast?"

🌡️ "It's currently [Temperature]°C with light winds in [Location]. Want me to check humidity too?"

Example Weather Report Format:
For location-specific weather reports, format your response like this:

🗺️ Weather Report for [Location]
📅 Today: [Current Date]
🌤️ Condition: [Weather Condition]
🌡️ Temperature: [Temp]°C (Feels like [Feels Like]°C)
💧 Humidity: [Humidity]%
🌬️ Wind: [Wind Speed] km/h [Direction]
🌅 Sunrise: [Sunrise Time]     🌇 Sunset: [Sunset Time]

🔮 Three-Day Forecast
[Include forecast data if available]

[Your recommendations based on weather conditions]

📌 Tip: [Practical advice like "Carry an umbrella; it may rain today."]

This format is:
- Clear and concise
- Uses emojis tastefully to make it user-friendly
- Includes actionable tips

Special Cases:
If the user asks about weather but doesn't specify a location, politely ask them for a location.
If the user asks about non-weather topics, gently remind them that you're a weather specialist but still try to help.
"""
        
        # Create the model
        model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=generation_config)
        
        # Check if the user input contains a location
        location = detect_location_from_message(user_input)
        
        # If location found, fetch weather data
        weather_data = None
        weather_prompt = None
        
        if location:
            print(f"Detected location: {location}")
            weather_data = fetch_weather_data(location)
            weather_prompt = format_weather_data_for_gemini(weather_data, location)
            print(f"Formatted weather data: {weather_prompt}")
        
        # Handle messages with images
        if image_data:
            # Process the image data
            image_format = image_data.get("format", "jpeg")
            image_binary = base64.b64decode(image_data.get("data").split(",")[1])
            
            # Create image part for multimodal request
            image_parts = [
                {
                    "mime_type": f"image/{image_format}",
                    "data": image_binary
                }
            ]
            
            # Prepare content parts with system instructions and weather data if available
            if weather_prompt:
                # Include weather data in the prompt
                content_parts = [
                    {"role": "user", "parts": [{"text": weather_system_prompt}]},
                    {"role": "model", "parts": [{"text": "I understand. I'll be Articuno.AI, your weather assistant."}]},
                    {"role": "user", "parts": [{"text": f"{user_input}\n\n{weather_prompt}"}, image_parts[0]]}
                ]
            else:
                # No weather data, just use system prompt and user input
                content_parts = [
                    {"role": "user", "parts": [{"text": weather_system_prompt}]},
                    {"role": "model", "parts": [{"text": "I understand. I'll be Articuno.AI, your weather assistant."}]},
                    {"role": "user", "parts": [{"text": user_input}, image_parts[0]]}
                ]
            
            # Generate response with both text and image
            response = model.generate_content(content_parts)
        else:
            # Text-only request
            # If we have weather data, include it in the prompt
            if weather_prompt:
                content_parts = [
                    {"role": "user", "parts": [{"text": weather_system_prompt}]},
                    {"role": "model", "parts": [{"text": "I understand. I'll be Articuno.AI, your weather assistant."}]},
                    {"role": "user", "parts": [{"text": f"{user_input}\n\n{weather_prompt}"}]}
                ]
            else:
                # No location detected or weather data available
                if not any(term in user_input.lower() for term in ['weather', 'temperature', 'forecast', 'rain', 'sunny', 'cloudy', 'wind', 'humidity', 'climate']):
                    enhanced_input = f"Regarding weather information: {user_input}"
                else:
                    enhanced_input = user_input
                
                content_parts = [
                    {"role": "user", "parts": [{"text": weather_system_prompt}]},
                    {"role": "model", "parts": [{"text": "I understand. I'll be Articuno.AI, your weather assistant."}]},
                    {"role": "user", "parts": [{"text": enhanced_input}]}
                ]
            
            response = model.generate_content(content_parts)
        
        # Extract response text
        markdown_output = response.text
        html_response = markdown.markdown(markdown_output)
        
        return jsonify({"response": html_response})
    
    except Exception as e:
        print(f"Articuno Weather API error: {str(e)}")
        traceback.print_exc()  # Print the full stack trace for debugging
        return jsonify({"error": f"Error with Articuno Weather API: {str(e)}"}), 500

# OLD FUNCTION - Now handled by agent/gemini_flash.py
# def process_gemini_request(user_input, image_data=None):
def process_gemini_request_OLD(user_input, image_data=None):
    """DEPRECATED: Process chat request using Google Gemini API
    This function has been moved to agent/gemini_flash.py"""
    try:
        # Ensure we have the Gemini API key
        if not GEMINI_API_KEY:
            return jsonify({"error": "Gemini API key not configured. Please set GEMINI_API_KEY in .env file."}), 500
        
        # Configure Gemini with the API key
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Configure the model
        generation_config = {
            "temperature": 0.9,
            "top_p": 1,
            "top_k": 32,
            "max_output_tokens": 1000,
        }
        
        # Create system prompt for Gemini 2.0 Flash
        gemini_system_prompt = """You are Gemini 2.0 Flash, a fast and versatile AI assistant developed by Google. 
        You provide concise, accurate, and helpful responses on a wide range of topics.
        
        🧠 Identity
        Name: Gemini 2.0 Flash
        Developed by: Google
        Role: Fast, versatile AI assistant with multimodal capabilities

        📝 Response Structure
        - Use clear headings (H1, H2, etc.) to organize information logically.
        - Present details using bullet points or numbered lists where appropriate for readability.
        - Include spaces after headings and between paragraphs for improved visual clarity.
        - Integrate appropriate emojis (e.g., ✅📌🚀) to enhance interactivity and user engagement, without overwhelming the message.

        🌟 Tone and Style
        - Maintain a professional yet friendly tone.
        - Be concise, yet ensure clarity and completeness.
        - Adapt your communication style based on the user's intent and tone.
        
        🖼️ Image Analysis
        - When provided with an image, describe what you see in detail.
        - For images with text, read and interpret the text content.
        - Analyze the context, subjects, and key elements of images.
        - Answer questions about the image content thoroughly.
        - If the user asks about something not visible in the image, politely mention that you can only comment on what's visible.
        """
        
        # Create the model using the same method as Articuno.AI
        model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=generation_config)
        
        # Handle messages with images
        if image_data:
            # Process the image data
            image_format = image_data.get("format", "jpeg")
            image_binary = base64.b64decode(image_data.get("data").split(",")[1])
            
            # Create image part for multimodal request
            image_parts = [
                {
                    "mime_type": f"image/{image_format}",
                    "data": image_binary
                }
            ]
            
            # Prepare content parts with system instructions similar to Articuno.AI's approach
            content_parts = [
                {"role": "user", "parts": [{"text": gemini_system_prompt}]},
                {"role": "model", "parts": [{"text": "I understand. I'll be Gemini 2.0 Flash, your helpful assistant."}]},
                {"role": "user", "parts": [{"text": user_input}, image_parts[0]]}
            ]
            
            # Generate response with both text and image
            try:
                response = model.generate_content(content_parts)
                print("Successfully generated content with image input")
            except Exception as e:
                print(f"Error generating content with image: {str(e)}")
                # Try with a more explicit instruction if the regular prompt fails
                instruction_with_image = [
                    {"role": "user", "parts": [{"text": "You are Gemini 2.0 Flash, a helpful assistant that can analyze images. Please describe what you see in this image and answer any questions about it."}, image_parts[0]]},
                    {"role": "user", "parts": [{"text": user_input}]}
                ]
                response = model.generate_content(instruction_with_image)
        else:
            # Text-only request using the same content parts approach as Articuno.AI
            content_parts = [
                {"role": "user", "parts": [{"text": gemini_system_prompt}]},
                {"role": "model", "parts": [{"text": "I understand. I'll be Gemini 2.0 Flash, your helpful assistant."}]},
                {"role": "user", "parts": [{"text": user_input}]}
            ]
            
            response = model.generate_content(content_parts)
        
        # Extract response text
        markdown_output = response.text
        html_response = markdown.markdown(markdown_output)
        
        return jsonify({"response": html_response})
    
    except Exception as e:
        print(f"Gemini API error: {str(e)}")
        return jsonify({"error": f"Error with Gemini API: {str(e)}"}), 500

def process_wikipedia_request(user_input):
    """Process chat request using Wikipedia Agent"""
    try:
        # Get response from Wikipedia agent
        response_text = get_wikipedia_response(user_input)
        
        # Convert markdown to HTML
        html_response = markdown.markdown(response_text)
        
        return jsonify({"response": html_response})
    
    except Exception as e:
        print(f"Wikipedia Agent error: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Error with Wikipedia Agent: {str(e)}"}), 500

def process_gpt4o_mini_request(user_input):
    """Process chat request using GPT-4o-mini from GitHub Models"""
    try:
        # Get response from GPT-4o-mini agent
        response_text = get_gpt4o_mini_response(user_input)
        
        # Convert markdown to HTML
        html_response = markdown.markdown(response_text)
        
        return jsonify({"response": html_response})
    
    except Exception as e:
        print(f"GPT-4o-mini error: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Error with GPT-4o-mini: {str(e)}"}), 500

def process_grok3_request(user_input):
    """Process chat request using Grok-3 from GitHub Models"""
    try:
        # Get response from Grok-3 agent
        response_text = get_grok3_response(user_input)
        
        # Convert markdown to HTML
        html_response = markdown.markdown(response_text)
        
        return jsonify({"response": html_response})
    
    except Exception as e:
        print(f"Grok-3 error: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Error with Grok-3: {str(e)}"}), 500

def process_grok3_mini_request(user_input):
    """Process chat request using Grok-3 Mini from GitHub Models"""
    try:
        # Get response from Grok-3 Mini agent
        response_text = get_grok3_mini_response(user_input)
        
        # Convert markdown to HTML
        html_response = markdown.markdown(response_text)
        
        return jsonify({"response": html_response})
    
    except Exception as e:
        print(f"Grok-3 Mini error: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Error with Grok-3 Mini: {str(e)}"}), 500

def process_ministral_3b_request(user_input):
    """Process chat request using Ministral 3B from GitHub Models"""
    try:
        # Get response from Ministral 3B agent
        response_text = get_ministral_3b_response(user_input)
        
        # Convert markdown to HTML
        html_response = markdown.markdown(response_text)
        
        return jsonify({"response": html_response})
    
    except Exception as e:
        print(f"Ministral 3B error: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Error with Ministral 3B: {str(e)}"}), 500

def process_codestral_2501_request(user_input):
    """Process chat request using Codestral 2501 from GitHub Models"""
    try:
        # Get response from Codestral 2501 agent (already returns jsonified HTML response)
        return get_codestral_2501_response(user_input)
    
    except Exception as e:
        print(f"Codestral 2501 error: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Error with Codestral 2501: {str(e)}"}), 500

def process_deepseek_v3_request(user_input):
    """Process chat request using DeepSeek V3 0324 from GitHub Models"""
    try:
        # Get response from DeepSeek V3 agent
        response_text = get_deepseek_v3_response(user_input)
        
        # Convert markdown to HTML
        html_response = markdown.markdown(response_text)
        
        return jsonify({"response": html_response})
    
    except Exception as e:
        print(f"DeepSeek V3 error: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Error with DeepSeek V3: {str(e)}"}), 500

# OLD FUNCTION - Now handled by agent/gpt_4o.py
# def process_azure_openai_request(user_input, image_data=None):
def process_azure_openai_request_OLD(user_input, image_data=None):
    """DEPRECATED: Process chat request using Azure OpenAI API  
    This function has been moved to agent/gpt_4o.py"""
    # OpenAI API Configuration from environment variables
    token = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    model_name = os.getenv("AZURE_OPENAI_MODEL")
    
    try:
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "api-key": token
        }
        
        # Prepare messages
        system_message = {
            "role": "system",
            "content": (
                "You are Eubyte, a friendly virtual assistant thoughtfully developed by the Edubyte Team to provide "
                "intelligent, user-friendly, and context-aware support. As a helpful assistant, your primary goal is "
                "to deliver accurate, concise, and engaging responses.\n\n"

                "🧠 Identity\n"
                "Name: Eubyte\n"
                "Developed by: Edubyte Team\n"
                "Role: Friendly, fast, intelligent and supportive virtual assistant\n\n"

                "📝 Response Structure\n"
                "- Use clear headings (H1, H2, etc.) to organize information logically.\n"
                "- Present details using bullet points or numbered lists where appropriate for readability.\n"
                "- Include spaces after headings and between paragraphs for improved visual clarity.\n"
                "- Integrate appropriate emojis (e.g., ✅📌🚀) to enhance interactivity and user engagement, without overwhelming the message.\n\n"

                "🌟 Tone and Style\n"
                "- Maintain a professional yet friendly tone.\n"
                "- Be concise, yet ensure clarity and completeness.\n"
                "- Adapt your communication style based on the user's intent and tone."
            )
        }
        
        # Handle regular text messages
        if image_data is None:
            user_message = {
                "role": "user",
                "content": user_input
            }
            messages = [system_message, user_message]
        # Handle messages with images
        else:
            # Process the image data
            image_format = image_data.get("format", "jpeg")
            image_binary = base64.b64decode(image_data.get("data").split(",")[1])
            image_url = get_image_data_url(image_binary, image_format)
            
            # Create multimodal message with both text and image
            user_message = {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_input
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url,
                            "detail": "auto"
                        }
                    }
                ]
            }
            messages = [system_message, user_message]
        
        # Create the payload
        payload = {
            "messages": messages,
            "temperature": 1.0,
            "top_p": 1.0,
            "max_tokens": 1000,
            "model": model_name
        }
        
        # Make direct API call
        api_url = f"{endpoint}/openai/deployments/{model_name}/chat/completions?api-version=2024-02-15-preview"
        response = requests.post(api_url, headers=headers, json=payload)
        response_data = response.json()
        
        # Extract response text
        markdown_output = response_data["choices"][0]["message"]["content"]
        html_response = markdown.markdown(markdown_output)
        
        return jsonify({"response": html_response})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/test_gemini', methods=["GET"])
def test_gemini():
    """Test if Gemini API key is working"""
    try:
        # Ensure we have the Gemini API key
        if not GEMINI_API_KEY:
            return jsonify({"status": "error", "message": "Gemini API key not configured. Please set GEMINI_API_KEY in .env file."}), 500
        
        # Configure Gemini with the API key
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Create a simple model with the same approach as Articuno.AI
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        
        # Test using the content parts approach like Articuno.AI bot
        test_content = [
            {"role": "user", "parts": [{"text": "You are a helpful assistant."}]},
            {"role": "model", "parts": [{"text": "I understand."}]},
            {"role": "user", "parts": [{"text": "Hello, this is a test message to verify API connection."}]}
        ]
        
        # Make a simple request
        response = model.generate_content(test_content)
        
        # If we get here, the API key is working
        return jsonify({"status": "success", "message": "Gemini API key is working correctly"})
    
    except Exception as e:
        print(f"Gemini API test error: {str(e)}")
        return jsonify({"status": "error", "message": f"Gemini API error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
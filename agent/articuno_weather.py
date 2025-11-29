import os
import re
import requests
import markdown
from flask import jsonify
import google.generativeai as genai
from dotenv import load_dotenv
import base64
import traceback

# Load environment variables
load_dotenv()

# Configure Google Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Configure OpenWeather API
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"


def detect_location_from_message(message):
    """
    Extracts location information from a user message.
    
    Args:
        message (str): The user message to analyze
        
    Returns:
        str or None: Detected location name or None if no location found
    """
    # Enhanced location detection - look for common location query patterns
    location_patterns = [
        r"weather\s+(?:in|at|for)\s+([A-Za-z\s,]+)",  # "weather in London"
        r"(?:in|at)\s+([A-Za-z\s,]+?)(?:\s+weather|\?|$)",  # "in Paris weather"
        r"^([A-Za-z\s,]+?)(?:\s+weather|\?|$)",  # "Tokyo weather"
        r"^([A-Za-z\s,]+?)$",  # Just the location name
        r"weather (?:of|for|in|at)\s+([A-Za-z\s,]+)",  # "weather of Tokyo"
        r"weather(?:.+?)(?:of|for|in|at)\s+([A-Za-z\s,]+)",  # "weather report of London"
        r"(?:show|get|tell|give)(?:.+?)weather(?:.+?)(?:of|for|in|at)\s+([A-Za-z\s,]+)",  # "give me weather of London"
        r"(?:show|get|tell|give)(?:.+?)(?:of|for|in|at)\s+([A-Za-z\s,]+?)(?:\s+weather|\?|$)",  # "give me of London weather"
        r"(?:how is|what is|what's)(?:.+?)weather(?:.+?)(?:of|for|in|at)\s+([A-Za-z\s,]+)",  # "how is the weather in London"
        r"(?:how's|what's)(?:.+?)(?:of|for|in|at)\s+([A-Za-z\s,]+?)(?:\s+weather|\?|$)",  # "what's in London weather like"
        r"(?:temperature|forecast|climate|humidity|wind|conditions)(?:.+?)(?:in|at|for)\s+([A-Za-z\s,]+)",  # "temperature in Berlin"
        r"(?:will it rain|is it sunny|is it hot|is it cold)(?:.+?)(?:in|at)\s+([A-Za-z\s,]+)",  # "will it rain in Seattle"
        r"what's the (?:weather|temperature|forecast)(?:.+?)(?:in|at|for)\s+([A-Za-z\s,]+)"  # "what's the forecast for Chicago"
    ]
    
    for pattern in location_patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            location = match.group(1).strip()
            # Remove trailing punctuation if any
            location = re.sub(r'[.,;:!?]+$', '', location)
            return location
    
    # As a fallback, try to find any city name mentioned in the query
    # This is a simple approach - in a production system, you might use NER (Named Entity Recognition)
    words = message.split()
    for word in words:
        # Clean the word of punctuation
        clean_word = re.sub(r'[.,;:!?]+$', '', word)
        # If the word starts with a capital letter and is at least 3 characters, it might be a location
        if len(clean_word) >= 3 and clean_word[0].isupper() and clean_word.lower() not in [
            "what", "where", "when", "why", "how", "can", "could", "would", 
            "should", "will", "shall", "the", "this", "that", "these", "those",
            "give", "show", "tell", "about", "weather", "forecast", "temperature",
            "conditions", "articuno", "hello", "thanks", "thank", "please", "good",
            "morning", "afternoon", "evening", "night", "today", "tomorrow", "yesterday"
        ]:
            return clean_word
    
    return None


def fetch_weather_data(location):
    """
    Fetches weather data from OpenWeather API for a specific location.
    
    Args:
        location (str): The location to fetch weather data for
        
    Returns:
        dict: Weather data for the location or error information
    """
    try:
        # Fetch current weather
        current_url = f"{OPENWEATHER_BASE_URL}/weather"
        params = {
            "q": location,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"  # Use metric units (Celsius)
        }
        
        response = requests.get(current_url, params=params)
        if response.status_code != 200:
            return {"error": f"Weather API error: {response.status_code} - {response.json().get('message', 'Unknown error')}"}
        
        current_data = response.json()
        
        # Fetch forecast (5 days / 3 hours)
        forecast_url = f"{OPENWEATHER_BASE_URL}/forecast"
        forecast_response = requests.get(forecast_url, params=params)
        
        if forecast_response.status_code != 200:
            return {
                "current": current_data,
                "forecast_error": f"Forecast API error: {forecast_response.status_code}"
            }
        
        forecast_data = forecast_response.json()
        
        # Return combined weather data
        return {
            "current": current_data,
            "forecast": forecast_data
        }
    except Exception as e:
        return {"error": f"Error fetching weather data: {str(e)}"}


def format_weather_data_for_gemini(weather_data, location):
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


def get_articuno_weather_response(user_input, image_data=None):
    """
    Get response from Articuno.AI weather assistant for web application.
    
    Args:
        user_input (str): The user's input message
        image_data (dict, optional): Image data if provided
        
    Returns:
        dict: JSON response with HTML-formatted response or error
    """
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


# For testing in terminal (when run directly)
if __name__ == "__main__":
    test_message = "What's the weather in London?"
    print(f"User: {test_message}")
    response = get_articuno_weather_response(test_message)
    print(f"Articuno.AI: {response}")
